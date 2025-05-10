import asyncio
from typing import List
from bson import ObjectId
import httpx
from spire.doc import *
from fastapi import Depends
from app.repository.file import FileRepository, get_file_repo
from app.repository.chrome import ChromaRepository, get_chroma_repo
from app.core.log import Logger
import pymupdf 
from app.domain.file import Context, Chunk

class FileService:
    def __init__(self, repoChroma: ChromaRepository, repoMongo: FileRepository):
        self.repoChroma = repoChroma
        self.repoMongo = repoMongo
    
    async def embend(self, input: List[str]):
        async with httpx.AsyncClient(timeout=None) as client:

                embend = await client.post(
                    "http://ollama-service:8000/embendding",
                    json=input
                )

                embend = embend.json()
                return embend
    
    async def upload_text_file(self, chat_id: str, filename: str) -> List[str]:
        """
        Основная идея: 
        1. Получить текст каждой страницы
        2. Текст разделить на чанки по 500 символов с пересечение по 50 символов для логической связи, чтобы Embendding LLM не "захлебнулась"
        3. Заранее определить все нужные поля, ids в ChromaDB это _id из всех документов MongoDB заранее определенные и сохранить все в список files: List[File]
        4. Сделать эмбенддинг для всех чанков
        5. Cохранять чанки в ChromaDB и MongoDB
        """
        try:
            path = os.path.join("temp_uploads", filename)

            doc = pymupdf.open(path)
            chunks: List[Chunk] = []
            ids = []

            for _, page in enumerate(doc): # enumerate  для debug и вывода id 
                text = page.get_text()
                
                for i in range(0, len(text), 450): # разбиваем текст страницы на чанки по 500 символом с пересечение по 50 символом
                    chunkDB = Chunk(id=str(ObjectId()),
                                  chat_id=chat_id,
                                  filename=filename,
                                  chunk_index=i//450,
                                  text=text[i:i+500])
                   
                    chunks.append(chunkDB) # чтобы не каждый чанк эмбенддить и сохранять в БД две, группируем по 500 элементов и сохраняем потом
                    ids.append(chunkDB.id)

                
                if len(chunks)>500: # по кускам отправляем в модели
                    # параллельно запускаем эмбенддинг и сохранение в Mongo 
                    embedding_task = asyncio.create_task(self.embed(input=[c.text for c in chunks])) # делаем эмбенддинг с помощью ollama
                    mongo_task = asyncio.create_task(self.repoMongo.create_chunks(chunks)) # сохраняем в MongoDB. P.S. изначально должно было возвращать ids, которые затем использовались бы в ChromaDB

                    

                    # ждем эмбенддинг и сохраняем в ChromeDB
                    response = await embedding_task 
                    embeddings = response["embeddings"]

                    chroma_task = asyncio.create_task(self.repoChroma.save(chunks=chunks, embeddings=embeddings))  # используются внутри заранее определенные ids и другие поля в предыдущем цикле где id=str(ObjectId())
                                                                                                                    # так как все асинхронно это позволит асинхронно добавлять и в Mongo и в ChromaDB
                    # ждем всех
                    await asyncio.gather(mongo_task, chroma_task)

                    # обнуляем чтоб не дублировать
                    chunks = []

            # если что-то осталось делаем те же самые действия        
            if chunks:
                embedding_task = asyncio.create_task(self.embend([c.text for c in chunks])) # делаем эмбенддинг с помощью ollama
                mongo_task = asyncio.create_task(self.repoMongo.create_chunks(chunks)) # сохраняем в MongoDB. P.S. изначально должно было возвращать ids, которые затем использовались бы в ChromaDB
                
                

                # сохраняем в ChromeDB
                response = await embedding_task 
                embeddings = response["embeddings"]

                chroma_task = asyncio.create_task(self.repoChroma.save(chunks=chunks, embeddings=embeddings))  # используются внутри заранее определенные ids и другие поля в предыдущем цикле где id=str(ObjectId())
                                                                                                                # так как все асинхронно это позволит асинхронно добавлять и в Mongo и в ChromaDB

                await asyncio.gather(mongo_task, chroma_task)
                # обнуляем чтоб не дублировать
                chunks = []

            return ids
        except Exception as e:
            raise Exception(f"file service: upload text: {e}")

    async def get_context(self, context: Context) -> Context:
        try:
            # делаем эмбенддинг для промпта 
            response = await self.embed(input=context.prompt)
            embeddings = response["embeddings"]

            # поиск нужных даннвх по чату
            contextRepo = await self.repoChroma.query(context.ids, 3, embeddings)

            context.context = contextRepo
            return context
        except Exception as e:
            raise Exception(f"file service: get context: {e}")
        
            
def get_file_service(repoChroma: ChromaRepository = Depends(get_chroma_repo), repoMongo: FileRepository = Depends(get_file_repo)):
    return FileService(repoChroma=repoChroma, repoMongo=repoMongo)