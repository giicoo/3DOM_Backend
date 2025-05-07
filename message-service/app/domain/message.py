from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal

@dataclass
class Message:
    id: str = None
    chat_id: str = None
    parent_id: str = None
    res_ids: List[str] = None
    role: Literal["user", "assistant", "system"] = None
    content: str = None
    created_at: datetime = field(default_factory=datetime.now)
