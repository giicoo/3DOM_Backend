

from contextlib import asynccontextmanager
import time

from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.error import APIError
from app.core.database import close_mongo_connection, connect_to_mongo
from app.core.environment import API_VERSION, APP_NAME
from app.core.log import Logger
from app.schemas.chat import ChatDocument
from app.api.v1.chat import ChatRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await connect_to_mongo()
    app.state.mongo_client = client
    await init_beanie(client["db"], document_models=[ChatDocument])
    yield 
    await close_mongo_connection(client)



app = FastAPI(
    title=APP_NAME + " chat service",
    version=API_VERSION,
    lifespan=lifespan
)


@app.exception_handler(APIError)
async def exception_handler(request: Request, exc: APIError):
    """
    Для собственных ошибок  
    """
    Logger.error(f"APIError: {exc}")
    return JSONResponse(
        status_code=exc.code,
        content={"error": f"{exc}"},
    )

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """
    Для системных ошибок
    """
    Logger.error(f"SYSTEM ERROR: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal error: {exc}"},
    )

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        body = await request.json()
    except:
        body = ""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    Logger.info({"request-path":request.path_params, "request-query": request.query_params.multi_items(), "body": body, "process_time":process_time, "response":response})
    return response

app.include_router(ChatRouter)
