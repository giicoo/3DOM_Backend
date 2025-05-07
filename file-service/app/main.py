

from contextlib import asynccontextmanager
import time

from beanie import init_beanie
from fastapi import FastAPI, Request

from app.core.database import close_mongo_connection, connect_to_chrome, connect_to_mongo
from app.core.environment import API_VERSION, APP_NAME
from app.core.log import Logger
from app.schemas.file import FileDocument
from app.api.v1.file import FileRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await connect_to_mongo()
    app.state.mongo_client = client
    await init_beanie(client["db"], document_models=[FileDocument])
    chrome_coll = await connect_to_chrome()
    app.state.chrome_client = chrome_coll
    yield 
    await close_mongo_connection(client)



app = FastAPI(
    title=APP_NAME,
    version=API_VERSION,
    lifespan=lifespan
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

app.include_router(FileRouter)
