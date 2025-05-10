from typing import List
from fastapi import Depends
import httpx
from app.domain.message import Message
from app.repository.message import MessageRepository, get_msg_repo
from app.core.environment import OLLAMA_URI

class MessageService:
    def __init__(self, repo: MessageRepository):
        self.repo = repo
    
    async def create_message(self, msg: Message) -> str:
        try:
            # перекидываю зависимости на файлы, если у родителей они были
            parent_message = await self.repo.get_message(msg.parent_id)
            if parent_message.res_ids:
                msg.res_ids += parent_message.res_ids

            return await self.repo.create_message(msg)
        except Exception as e:
            raise Exception(f"message service: create message: {e}")
        
    async def get_message(self, id: str) -> Message:
        try:
            return await self.repo.get_message(id)
        except Exception as e:
            raise Exception("message service: get message: {e}")
    
    async def get_branch_messages(self, id: str) -> List[Message]:
        """
        Рекурсивно получаю каждое родительское сообщение поднимаясь вверх до parent_id = null 

        Пример схема: 

        __________________________________________
            |id=1; parent_id=null|

                        /     \ 

        |id=2; parent_id=1|  |id=3; parent_id=1|
                |
        |id=4; parent_id=2| 

        __________________________________________
        
        Если get_branch_messages(4):
        1. Получаем id=4
        2. По parent_id=2 получаем id=2
        3. По parent_id=1 получаем id=1

        Возвращаем [id=1, id=2, id=4]
        """
        
        messages = []
        message = await self.repo.get_message(id)
        messages.append(message)
        while message.parent_id:
            message = await self.repo.get_message(message.parent_id)
            messages = [message] + messages

        return messages
    
    async def get_all(self, chat_id:str) -> List[Message]:
        messages = await self.repo.get_messages(chat_id=chat_id)
        return messages
    
    async def stream(self, id: str):
        """
        Вызывается после create_message, получая id последнего добавленного сообщения, получаем необходимую ветку.
        Генерируем ответ и сохраняем новое сообщение с parent_id=id
        """
        messages = await self.get_branch_messages(id)
        message = messages[-1]
        model = ""

        async with httpx.AsyncClient(timeout=None) as client:

                chat = await client.get(
                    f"http://chat-service:8000/get/{str(message.chat_id)}",
                )

                chat = chat.json()
                model = chat["model"]

        async with httpx.AsyncClient(timeout=None) as client:

            context = await client.post(
                "http://file-service:8000/get_context",
                json= {
                    "ids": [str(i) for i in message.res_ids],
                    "prompt": message.content
                }
            )
            context = context.json()["context"]



            async with client.stream(
                "POST",
                "http://ollama-service:8000/stream",
                json={
                    "model": model,
                    "msgs": [
                        {"role":m.role, "content":m.content} for m in messages
                    ],
                    "context": context
                },
                headers={"Accept": "text/event-stream"}
            ) as response:
                full_response=""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        full_response+=line.removeprefix("data: ")
                        yield line.removeprefix("data: ")
        ida = await self.create_message(Message(chat_id=str(message.chat_id), role="assistant", content=full_response, parent_id=id, res_ids=[str(i) for i in message.res_ids]))
        yield f"ID: {ida}"
            
def get_msg_service(repo: MessageRepository = Depends(get_msg_repo)):
    return MessageService(repo)