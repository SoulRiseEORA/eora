from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from .schema import MemoryRecord
from .store import JsonMemoryStore
from .edges import auto_connect


async def store_and_connect(
    user_id: str,
    text: str,
    sub_topic: Optional[str] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
) -> str:
    """사용자별 폴더에 메모리를 저장하고, 자동 연결을 수행한다.
    반환: 생성된 memory_id
    """
    now_iso = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    record = MemoryRecord(
        user_id=user_id or "anonymous",
        scope="long_term",
        type="doc",
        source={"sub_topic": sub_topic, **(extra_meta or {})},
        text=text or "",
        pin=False,
    )

    store = JsonMemoryStore()
    store.write(record)

    # auto_connect용 메모리 dict 구성
    mem_dict = {
        "memory_id": record.memory_id,
        "user_id": record.user_id,
        "text": text or "",
        "sub_topic": sub_topic,
        "time": {"observed_at": now_iso},
    }

    # 연결은 실패해도 서비스 흐름 방해하지 않도록 try
    try:
        await auto_connect([mem_dict])
    except Exception:
        pass

    return record.memory_id

