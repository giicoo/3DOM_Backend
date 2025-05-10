from typing import List
from app.core.environment import OLLAMA_URI
from ollama import AsyncClient, EmbedResponse
from app.domain.ollama import OllamaChat

class OllamaService:
    def __init__(self):
        self.client = AsyncClient(host="http://ollama:11434")
    
    async def generate_chat_title(self, query: str) -> str:
        try:
            prompt = f"""
                You are an assistant that generates short, clear chat titles based on the first message in a conversation.
                without unnecessary words and explanations, just the title.  Without quotation marks, punctuation marks and other unnecessary symbols
                Message: "{query}"

                Generate a concise chat title:
                """
            response = await self.client.chat(model="llama2", messages=[
                    {"role": "user", "content": prompt}
            ])
            title = response['message']['content'].strip()
            return title
        except Exception as e:
            raise Exception(f"ollama service: gen chat title: {e}")
        
    async def embedding(self, input: List[str]) -> EmbedResponse:
        try:
            response = await self.client.embed(model="nomic-embed-text", input=input)
            return response
        except Exception as e:
             raise Exception(f"ollama service: embedding: {e}")
    
    async def stream(self, chat: OllamaChat):
        chat.msgs.insert(0, {
            "role": "system",
            "content": (
                """
                Ты — умный, честный и полезный AI-ассистент. 
                Отвечай ясно, по существу и на русском языке. 
                Если вопрос неполный — уточни, не делай догадок. 
                Объясняй свои ответы, когда это полезно, и оформляй их с помощью markdown. 
                Если просят код, приводи аккуратные и понятные примеры с комментариями.
                """
            )
        })
        context_str = "\n\n".join(chat.context)
        chat.msgs.insert(
            -1,
            {"role": "user", "content": f"[Context]\n{context_str}"}
        )

        response = await self.client.chat(model=chat.model, messages=chat.msgs, stream=True)
        async for chunk in response:
            yield chunk['message']['content']
            
            
def get_ollama_service():
    return OllamaService()