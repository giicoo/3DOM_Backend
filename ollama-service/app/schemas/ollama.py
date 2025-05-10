from typing import Any, Dict, List, Literal, TypedDict
from pydantic import BaseModel

class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

class OllamaChatIn(BaseModel):
    model: str
    msgs: List[Message]
    context: List[str]