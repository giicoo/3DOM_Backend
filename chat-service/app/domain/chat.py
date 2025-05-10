

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Chat:
    id: str = None
    telegram_id: int = None
    title: str = None
    model: str = None
    token: str = None
    created_at: datetime = field(default_factory=datetime.now)
