

from dataclasses import dataclass
from typing import Any, Dict, List, Literal


@dataclass
class OllamaChat:
    model: str
    msgs: List[Dict[Literal["user", "assistant", "system"], Any]]
    context: List[str]