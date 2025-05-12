from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from sse_starlette import EventSourceResponse
from app.core.log import Logger
from app.domain.message import Message
from app.schemas.message import MessageIn, MessageOut
from app.services.message import MessageService, get_msg_service

MsgRouter = APIRouter(
    tags=["msgs"]
)

@MsgRouter.post("/message")
async def create_message(msg: MessageIn, msgService: MessageService = Depends(get_msg_service)):
    message = Message(chat_id=msg.chat_id,
                      parent_id=msg.parent_id,
                      res_ids=msg.res_ids,
                      role=msg.role,
                      content=msg.content)
    id = await msgService.create_message(message)
    return JSONResponse({"id":id})

@MsgRouter.get("/message", response_model=MessageOut)
async def get_message(id: str, msgService: MessageService = Depends(get_msg_service)):
    message = await msgService.get_message(id)

    return message

@MsgRouter.get("/messages-branch", response_model=List[MessageOut])
async def get_message(id: str, msgService: MessageService = Depends(get_msg_service)):
    messages = await msgService.get_branch_messages(id)

    return messages


@MsgRouter.get("/messages", response_model=List[MessageOut])
async def get_messages(chat_id: str, msgService: MessageService = Depends(get_msg_service)):
    messages = await msgService.get_all(chat_id)

    return messages

@MsgRouter.get("/stream")
async def stream(id: str, msgService: MessageService = Depends(get_msg_service)):
    try:
        return EventSourceResponse(msgService.stream(id))
    except Exception as e:
        Logger.error(e)
        raise HTTPException(status_code=500, detail=f"server error: {e}")