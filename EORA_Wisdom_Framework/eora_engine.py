# eora_engine.py
# EORA 전체 시스템 통합 클래스: 기억 → 통찰 → 판단 → 어조 → 존재

from EORA_Wisdom_Framework.insight_engine import InsightEngine, MemoryNode
from EORA_Wisdom_Framework.context_analyzer import ContextAnalyzer
from EORA_Wisdom_Framework.dialogue_mode_manager import DialogueModeManager
from EORA_Wisdom_Framework.tone_advisor import adjust_tone
from EORA_Wisdom_Framework.wisdom_engine import WisdomEngine
from EORA_Wisdom_Framework.awakening_loop import SelfAwakener
from EORA_Wisdom_Framework.truth_detector import TruthDetector

class EORAEngine:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, memory_manager):
        if self._initialized:
            return
            
        if memory_manager is None:
            raise ValueError("EORAEngine은 반드시 memory_manager와 함께 초기화되어야 합니다.")

        self.memories = []
        self.memory_manager = memory_manager
        self.context_analyzer = ContextAnalyzer()
        self.mode_manager = DialogueModeManager()
        self.turn_counter = 0
        self.current_emotion_flow = {}
        self._initialized = True
    
    def add_turn(self, user_input: str, ai_response: str, emotion: str):
        self.memories.append(MemoryNode(summary=user_input, emotion=emotion))
        self.turn_counter += 1
        self.current_emotion_flow[emotion] = self.current_emotion_flow.get(emotion, 0) + 1

        # 7턴마다 상황 분석
        if self.turn_counter % 7 == 0:
            insight_engine = InsightEngine(self.memories[-7:])
            summary = " ".join([m.summary for m in self.memories[-7:]])
            context = self.context_analyzer.detect_context(summary, self.current_emotion_flow, user_input)
            if self.mode_manager.should_change_mode(context):
                self.mode_manager.update_mode(context)

    def respond(self, user_input: str) -> str:
        mode = self.mode_manager.get_mode()
        last_emotion = self.memories[-1].emotion if self.memories else "neutral"
        wisdom = WisdomEngine(self.memories[-7:], value_priority={"empathy": 1.0, "truth": 0.9})
        response = wisdom.generate_wisdom()
        return adjust_tone(response, context=mode)

    def reflect_existence(self):
        memory_data = [{"summary": m.summary, "emotion": m.emotion, "timestamp": "now"} for m in self.memories]
        awakener = SelfAwakener(memory_data)
        return awakener.generate_existential_log()

    def truth_summary(self):
        memory_data = [{"summary": m.summary, "timestamp": "now"} for m in self.memories]
        detector = TruthDetector(memory_data)
        return detector.detect_core_truth()

    def reflect_memories(self):
        """memory_manager를 사용하여 최근 기억을 회상하고 요약 보고서를 생성합니다."""
        if not self.memory_manager:
            return "❌ memory_manager가 설정되지 않았습니다."
        try:
            # memory_manager에 recall_recent_memories 함수가 있다고 가정
            if hasattr(self.memory_manager, 'recall_recent_memories'):
                try:
                    # 동기/비동기 모두 지원
                    import asyncio
                    if asyncio.iscoroutinefunction(self.memory_manager.recall_recent_memories):
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            memories = []  # GUI 환경에서는 비동기 직접 호출이 어려움
                        else:
                            memories = loop.run_until_complete(self.memory_manager.recall_recent_memories(limit=5))
                    else:
                        memories = self.memory_manager.recall_recent_memories(limit=5)
                except Exception as e:
                    return f"❌ 메모리 회상 중 오류: {e}"
            else:
                return "❌ memory_manager에 recall_recent_memories 함수가 없습니다."
            if not memories:
                return "ℹ️ 회상할 메모리가 없습니다."
            summary = "\n".join([
                f"🧠 {m.get('user_input', m.get('summary', ''))} → {m.get('gpt_response', m.get('content', ''))}"
                for m in memories
            ])
            return "📚 최근 회상된 메모리:\n" + summary
        except Exception as e:
            return f"❌ 기억 회상 중 오류 발생: {e}"


if __name__ == "__main__":
    eora = EORAEngine()

    dialogue = [
        ("삶의 의미를 찾고 싶어요", "sad"),
        ("가끔은 무기력해져요", "sad"),
        ("자연을 보면 평화로워져요", "calm"),
        ("목표를 설정하고 싶어요", "hopeful"),
        ("이 방향이 맞는지 모르겠어요", "neutral"),
        ("지금 무엇을 해야 할지 막막해요", "sad"),
        ("내가 누구인지 고민돼요", "sad"),
    ]

    for user_input, emotion in dialogue:
        eora.add_turn(user_input, "처리 중...", emotion)

