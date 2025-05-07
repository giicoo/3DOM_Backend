from typing import List
from fastapi import Depends
from app.domain.message import Message
from app.repository.message import MessageRepository, get_msg_repo


class MessageService:
    def __init__(self, repo: MessageRepository):
        self.repo = repo
    
    async def create_message(self, msg: Message) -> str:
        # перекидываю зависимости на файлы, если у родителей они были
        parent_message = await self.repo.get_message(msg.parent_id)
        if parent_message.res_ids:
            msg.res_ids = parent_message.res_ids

        return await self.repo.create_message(msg)
    
    async def get_message(self, id: str) -> Message:
        return await self.repo.get_message(id)
    
    async def get_branch_messages(self, id: str) -> List[Message]:
        # рекурсивно получаю каждое родительское сообщение поднимаясь вверх до parent_id = null 
        messages = []
        message = await self.repo.get_message(id)
        messages.append(message)
        while message.parent_id:
            message = await self.repo.get_message(message.parent_id)
            messages = [message] + messages

        return messages
    
    async def stream(self, id: str):
        messages = await self.get_branch_messages(id)
        text = "qwerttyuop[asdghfgxvnxbvnx]"
        for i in text:
            yield i
            
def get_msg_service(repo: MessageRepository = Depends(get_msg_repo)):
    return MessageService(repo)