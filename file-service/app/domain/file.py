from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Context:
    ids: List[str] = None
    prompt: str = None
    context: List[str] = None

# @dataclass
# class File:
#     chat_id: str = None
#     path: str = None


@dataclass
class Chunk:
    id: str = None
    chat_id: str = None
    filename: str = None
    chunk_index: int = None
    text: str = None
    created_at: datetime = field(default_factory=datetime.now)




