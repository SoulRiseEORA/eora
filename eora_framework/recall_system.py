class RecallSystem:
    def __init__(self, memory_system):
        self.memory_system = memory_system

    def recall(self, query, mode="auto"):
        # 간단한 키워드 기반 회상 예시
        return [m for m in self.memory_system.memories if query in m["user"] or query in m["gpt"]]

    def recall_reason(self, memory_id):
        return f"Memory {memory_id} was recalled due to keyword match."

    def filter_by_emotion(self, emotion):
        return [m for m in self.memory_system.memories if m["emotion"] == emotion]

    def filter_by_chain(self, chain_id):
        return [m for m in self.memory_system.memories if m.get("parent_id") == chain_id] 