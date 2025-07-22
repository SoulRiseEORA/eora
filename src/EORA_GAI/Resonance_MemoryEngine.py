import json
from difflib import SequenceMatcher

class ResonanceMemoryEngine:
    def __init__(self, memory_path='data/memory_trace.json'):
        self.memory_path = memory_path
        self.memory = self.load_memory()

    def load_memory(self):
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                return json.load(f).get('loops', [])
        except:
            return []

    def find_resonant_memory(self, query):
        def similarity(a, b):
            return SequenceMatcher(None, a, b).ratio()

        matches = sorted(self.memory, key=lambda m: similarity(query, m["user_input"]), reverse=True)
        return matches[:3]  # 상위 3개 공명 기억 반환

    def print_resonant_memories(self, query):
        top_matches = self.find_resonant_memory(query)
        print(f"🔎 '{query}'와 공명하는 과거 기억:")
        for i, m in enumerate(top_matches, 1):
            print(f"{i}. [{m['timestamp']}] {m['user_input']} → 감정: {m['emotion_level']}, 충돌: {m['conflict']}")