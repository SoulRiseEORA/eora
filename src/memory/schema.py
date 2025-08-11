from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class MemoryRecord:
    memory_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = "anonymous"
    scope: str = "session"  # session|long_term|team|global
    type: str = "doc"  # fact|preference|task|decision|doc
    source: Dict[str, Any] = field(default_factory=dict)
    text: str = ""
    emb: Optional[List[float]] = None
    entities: List[str] = field(default_factory=list)
    time: Dict[str, Any] = field(default_factory=lambda: {
        "observed_at": now_iso(),
        "valid_from": None,
        "valid_to": None,
    })
    quality: Dict[str, Any] = field(default_factory=lambda: {
        "trust": 0.5,
        "recency_weight": 0.5,
        "stability": "stable",
    })
    privacy: Dict[str, Any] = field(default_factory=lambda: {
        "pii": False,
        "scope": "private",
    })
    version: int = 1
    ttl: Optional[int] = None
    pin: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "scope": self.scope,
            "type": self.type,
            "source": self.source,
            "text": self.text,
            "emb": self.emb,
            "entities": self.entities,
            "time": self.time,
            "quality": self.quality,
            "privacy": self.privacy,
            "version": self.version,
            "ttl": self.ttl,
            "pin": self.pin,
        }

