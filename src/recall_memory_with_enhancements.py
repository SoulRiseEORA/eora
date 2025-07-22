from aura_system.memory_store import get_memory_store

class RecallMemoryWithEnhancements:
    def __init__(self):
        self.memory_store = None

    async def initialize(self):
        try:
            self.memory_store = await get_memory_store()
        except Exception as e:
            print(f"메모리 스토어 초기화 실패: {str(e)}")
            self.memory_store = None 