class MemorySystem:
    def __init__(self):
        self.memories = []

    def store(self, user, gpt, emotion, belief_tags, **kwargs):
        memory = {
            "user": user,
            "gpt": gpt,
            "emotion": emotion,
            "belief_tags": belief_tags,
            "timestamp": kwargs.get("timestamp"),
            "memory_id": len(self.memories) + 1,
            "parent_id": kwargs.get("parent_id"),
            "resonance_score": kwargs.get("resonance_score", 0.0)
        }
        self.memories.append(memory)
        return memory["memory_id"]

    def chain(self, memory_id, parent_id):
        for m in self.memories:
            if m["memory_id"] == memory_id:
                m["parent_id"] = parent_id

    def get_emotion_trace(self):
        return [m["emotion"] for m in self.memories] 