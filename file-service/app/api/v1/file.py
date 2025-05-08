from io import BytesIO
import os
import shutil
from typing import List
from bson import ObjectId
from docx import Document
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, WebSocket
from fastapi.responses import JSONResponse
from pypdf import PdfReader
from sse_starlette import EventSourceResponse
from app.core.log import Logger
from app.services.file import FileService, get_file_service
from app.core.error import APIError
from app.schemas.file import ContextIn, ContextOut, Properties
from app.domain.file import Context

FileRouter = APIRouter(
    tags=["files"]
)




@FileRouter.post("/uploadfile/")
async def create_upload_file(chat_id: str = Form(..., examples=["5eb7cf5a86d9755df3a6c593"]), file: UploadFile = File(...), fileService: FileService = Depends(get_file_service)):
    properties = Properties(chat_id=chat_id)
    if file.content_type != "application/pdf":
            raise APIError(code=400, message="Неподдерживаемый файл. Используйте только pdf")
    
    temp_path = os.path.join("temp_uploads", file.filename)
    os.makedirs("temp_uploads", exist_ok=True)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if not os.path.exists(temp_path):
        # если какая ошибка при кодировке или в файловой системе
        raise APIError(code=400, message="Не можем определить файл. Попробуйте еще раз или поменяйте название на английский язык")

    
    await fileService.upload_text_file(chat_id=chat_id, filename=file.filename)
    os.remove(temp_path)
    return JSONResponse({"message":"ok"})


@FileRouter.post("/get_context", response_model=ContextOut)
async def get_context(context: ContextIn, fileService: FileService = Depends(get_file_service)):
    response = await fileService.get_context(Context(ids=[str(id) for id in context.ids], prompt=context.prompt))
    return response