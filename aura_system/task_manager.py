import asyncio
from typing import Set
from aura_system.logger import logger

# 전역 이벤트 루프
_loop = None

def get_event_loop():
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop

# 보류 중인 태스크 관리
_pending_tasks: Set[asyncio.Task] = set()

def add_task(task: asyncio.Task):
    """태스크를 보류 중인 태스크 목록에 추가합니다."""
    _pending_tasks.add(task)
    task.add_done_callback(_pending_tasks.discard)

async def cleanup_pending_tasks():
    """보류 중인 모든 태스크를 정리합니다."""
    if not _pending_tasks:
        return

    try:
        # 모든 태스크 취소
        for task in _pending_tasks:
            if not task.done():
                task.cancel()

        # 태스크 완료 대기
        await asyncio.gather(*_pending_tasks, return_exceptions=True)
        _pending_tasks.clear()
        logger.info("✅ 보류 중인 태스크 정리 완료")
    except Exception as e:
        logger.error(f"❌ 태스크 정리 중 오류 발생: {e}")

def get_pending_tasks() -> Set[asyncio.Task]:
    """현재 보류 중인 태스크 목록을 반환합니다."""
    return _pending_tasks.copy()

class TaskManager:
    def __init__(self):
        pass
    # TODO: 실제 구현 필요 