from .memory_system import MemorySystem
from .recall_system import RecallSystem
from .insight_engine import InsightEngine
from .wisdom_engine import WisdomEngine
from .truth_sense import TruthSense
from .self_realizer import SelfRealizer

class EORAFramework:
    def __init__(self):
        self.memory = MemorySystem()
        self.recall = RecallSystem(self.memory)
        self.insight = InsightEngine()
        self.wisdom = WisdomEngine()
        self.truth = TruthSense()
        self.self_realizer = SelfRealizer()

    def process(self, user_input, gpt_response, emotion, belief_tags, context=None):
        # 1. 기억 저장
        memory_id = self.memory.store(user=user_input, gpt=gpt_response, emotion=emotion, belief_tags=belief_tags)
        # 2. 회상
        memories = self.recall.recall(user_input)
        # 3. 통찰
        insight = self.insight.infer(memories)
        # 4. 지혜
        wise_response = self.wisdom.judge(insight, context, emotion)
        # 5. 진리
        truth = self.truth.detect(memories)
        # 6. 존재 감각
        identity = self.self_realizer.generate_identity(memories)
        # 7. 통합 리포트
        return {
            "wise_response": wise_response,
            "insight": insight,
            "truth": truth,
            "identity": identity
        } 