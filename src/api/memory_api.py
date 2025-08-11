from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from memory.schema import MemoryRecord
from memory.store import JsonMemoryStore


router = APIRouter(prefix="/api/memory", tags=["memory"])
store = JsonMemoryStore()


class MemoryUpsert(BaseModel):
    user_id: str = "anonymous"
    scope: str = "session"
    type: str = "doc"
    source: Dict[str, Any] = {}
    text: str
    entities: Optional[List[str]] = None
    pin: bool = False
    quality: Optional[Dict[str, Any]] = None


@router.post("/write")
async def write_memory(item: MemoryUpsert):
    rec = MemoryRecord(
        user_id=item.user_id,
        scope=item.scope,
        type=item.type,
        source=item.source,
        text=item.text,
        entities=item.entities or [],
        pin=item.pin,
    )
    if item.quality:
        rec.quality.update(item.quality)
    try:
        store.write(rec)
        return {"ok": True, "memory_id": rec.memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_memories(latest: bool = True):
    return store.read_latest_versions() if latest else store.read_all()

