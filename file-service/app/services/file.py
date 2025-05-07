from io import BytesIO
from itertools import batched
import shutil
from typing import List
from pypdf import PdfReader
from spire.doc import *
from fastapi import Depends, HTTPException, UploadFile
from app.repository.file import FileRepository, get_file_repo
from app.repository.chrome import ChromeRepository, get_chrome_repo
from docx import Document
from app.core.log import Logger


class FileService:
    def __init__(self, repo: ChromeRepository):
        self.repo = repo
    
    async def upload_text_file(self, path: str):
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                text = page.extract_text().split()
                for batch in batched(text, 500):
                    await self.repo.save(batch)


        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка при чтении файла: {str(e)}")


            
def get_file_service(repo: ChromeRepository = Depends(get_chrome_repo)):
    return FileService(repo)