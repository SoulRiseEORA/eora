from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from memory.edges import auto_connect


router = APIRouter(prefix="/api/edges", tags=["edges"]) 


class AutoConnectRequest(BaseModel):
    memories: List[Dict[str, Any]]  # memory_id/_id, text/content, time.observed_at, sub_topic 등 포함 권장
    window_hours: int = 2
    sim_top_k: int = 2
    sim_threshold: float = 0.85


@router.post("/auto")
async def build_edges(req: AutoConnectRequest):
    if not req.memories:
        raise HTTPException(status_code=400, detail="memories 필수")
    await auto_connect(
        req.memories,
        window_hours=req.window_hours,
        sim_top_k=req.sim_top_k,
        sim_threshold=req.sim_threshold,
    )
    return {"ok": True}

