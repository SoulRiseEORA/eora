import json
import os
import logging

# 현재 파일 기준 경로
BASE_PATH = os.path.dirname(__file__)

class EmotionLogicModule:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_emotion_maps()
        
    def _load_emotion_maps(self):
        try:
            with open(os.path.join(BASE_PATH, "emotion_keywords_map.json"), "r", encoding="utf-8") as f:
                self.EMOTION_KEYWORDS = json.load(f)
            
            with open(os.path.join(BASE_PATH, "emotion_code_map.json"), "r", encoding="utf-8") as f:
                self.EMOTION_CODES = json.load(f)
        except Exception as e:
            self.logger.error(f"감정 맵 로딩 실패: {str(e)}")
            self.EMOTION_KEYWORDS = {}
            self.EMOTION_CODES = {}

    def estimate_emotion(self, text: str):
        """
        텍스트에서 감정을 추정하는 메서드
        """
        score_dict = {}
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            count = sum(text.lower().count(k) for k in keywords)
            if count > 0:
                score_dict[emotion] = count

        if not score_dict:
            return "기타", "EXXX", 0.5

        best_emotion = max(score_dict, key=score_dict.get)
        weight = 0.5 + 0.1 * min(score_dict[best_emotion], 5)
        code = self.EMOTION_CODES.get(best_emotion, {}).get("code", "EXXX")

        return best_emotion, code, round(min(weight, 1.0), 3)

    def insert_emotion_message(self, emotion_label, emotion_code, base_prompt):
        """
        감정 기반 system 메시지를 삽입하는 메서드
        """
        return f"[이 대화의 감정은 '{emotion_label}' ({emotion_code})입니다.]\n{base_prompt}"

    def should_continue_emotion_convo(self, user_emotion_count, user_total_turns, system_emotion_turns):
        """
        감정 대화 비율 전략을 결정하는 메서드
        """
        ratio = (user_emotion_count / user_total_turns) if user_total_turns else 0
        system_emotion_ratio = system_emotion_turns / user_total_turns if user_total_turns else 0

        allow_continue = ratio >= 0.3 and system_emotion_ratio <= 0.2
        should_stop = system_emotion_ratio >= 0.25

        return allow_continue, should_stop

# 싱글톤 인스턴스
_emotion_logic_module = None

def get_emotion_logic_module():
    global _emotion_logic_module
    if _emotion_logic_module is None:
        _emotion_logic_module = EmotionLogicModule()
    return _emotion_logic_module
