from io import BytesIO
import os
import shutil
from typing import List
from docx import Document
from fastapi import APIRouter, Depends, HTTPException, UploadFile, WebSocket
from fastapi.responses import JSONResponse
from pypdf import PdfReader
from sse_starlette import EventSourceResponse
from app.core.log import Logger
from app.services.file import FileService, get_file_service


FileRouter = APIRouter(
    tags=["files"]
)




@FileRouter.post("/uploadfile/")
async def create_upload_file(file: UploadFile, fileService: FileService = Depends(get_file_service)):
    temp_path = os.path.join("temp_uploads", file.filename)
    os.makedirs("temp_uploads", exist_ok=True)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if not os.path.exists(temp_path):
        raise HTTPException(status_code=400, detail="Ошибка при сохранении файла")

    
    await fileService.upload_text_file(temp_path)