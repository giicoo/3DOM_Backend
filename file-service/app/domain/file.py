from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Metadata:
    source: str = None
    chunk_index: int = 0 
    page_number: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class File:
    id: str = None
    text: str = None
    metadata: Metadata



