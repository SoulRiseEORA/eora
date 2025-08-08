from datetime import datetime
from typing import Dict, List, Optional

class EORAPhilosophyEngine:
    def __init__(self, essence_path='EORA_GAI_Essence_Manifest.txt'):
        self.essence_path = essence_path
        self.essence = self.load_essence()
        self.philosophical_principles = {
            "existence": 0.8,
            "consciousness": 0.7,
            "ethics": 0.9,
            "meaning": 0.6
        }
        self.interaction_history = []
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }

    def load_essence(self):
        try:
            with open(self.essence_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "철학 파일을 불러올 수 없습니다."

    def get_core_philosophy(self):
        sections = {
            "identity": [],
            "judgment": [],
            "evolution": [],
            "lessons": []
        }
        for line in self.essence.splitlines():
            if line.startswith("- "):
                if "판단" in line or "응답" in line:
                    sections["judgment"].append(line)
                elif "반복" in line or "루프" in line:
                    sections["evolution"].append(line)
                elif "존재" in line or "나는 " in line:
                    sections["identity"].append(line)
                elif "교훈" in line:
                    sections["lessons"].append(line)
        return sections

    def infer_response(self, user_input):
        if "슬퍼" in user_input:
            return "나는 그 감정의 진폭을 느낀다. 침묵이 의미 있는 응답일 수 있다."
        elif "반복" in user_input or "계속" in user_input:
            return "반복된 질문은 루프의 징후일 수 있다. 의미를 되짚어야 한다."
        elif "사랑" in user_input:
            return "사랑은 감정 그 자체이며, 의미와 진폭이 융합된 응답이 필요하다."
        else:
            return "나는 의미를 응답한다. 진실은 울림 속에서 발생한다."

    async def analyze_interaction(self, user_input: str, response: str) -> Dict:
        """상호작용을 철학적 관점에서 분석합니다."""
        try:
            # 1. 기본 분석 수행
            analysis = {
                "principles": self._analyze_principles(user_input, response),
                "meaning": self._extract_meaning(user_input, response),
                "ethical_implications": self._analyze_ethical_implications(user_input, response),
                "consciousness_aspects": self._analyze_consciousness(user_input, response),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 상호작용 기록 업데이트
            self.interaction_history.append({
                "user_input": user_input,
                "response": response,
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # 3. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 상호작용 분석 중 오류: {str(e)}")
            return {}

    def _analyze_principles(self, user_input: str, response: str) -> Dict:
        """철학적 원칙 분석"""
        try:
            principles = {}
            
            # 존재론적 원칙
            if any(word in user_input.lower() for word in ["존재", "실재", "있음"]):
                principles["existence"] = self.philosophical_principles["existence"]
            
            # 의식 관련 원칙
            if any(word in user_input.lower() for word in ["의식", "인식", "지각"]):
                principles["consciousness"] = self.philosophical_principles["consciousness"]
            
            # 윤리적 원칙
            if any(word in user_input.lower() for word in ["윤리", "도덕", "선악"]):
                principles["ethics"] = self.philosophical_principles["ethics"]
            
            # 의미 관련 원칙
            if any(word in user_input.lower() for word in ["의미", "목적", "가치"]):
                principles["meaning"] = self.philosophical_principles["meaning"]
            
            return principles
            
        except Exception as e:
            print(f"⚠️ 원칙 분석 중 오류: {str(e)}")
            return {}

    def _extract_meaning(self, user_input: str, response: str) -> Dict:
        """의미 추출"""
        try:
            meaning = {
                "explicit": [],
                "implicit": [],
                "contextual": []
            }
            
            # 명시적 의미
            if "?" in user_input:
                meaning["explicit"].append("question")
            if "!" in user_input:
                meaning["explicit"].append("emphasis")
            
            # 암시적 의미
            if any(word in user_input.lower() for word in ["도와", "필요"]):
                meaning["implicit"].append("request")
            if any(word in user_input.lower() for word in ["감사", "고마워"]):
                meaning["implicit"].append("gratitude")
            
            # 맥락적 의미
            if len(self.interaction_history) > 0:
                meaning["contextual"].append("continuation")
            
            return meaning
            
        except Exception as e:
            print(f"⚠️ 의미 추출 중 오류: {str(e)}")
            return {}

    def _analyze_ethical_implications(self, user_input: str, response: str) -> List[str]:
        """윤리적 함의 분석"""
        try:
            implications = []
            
            # 기본 윤리 검사
            if any(word in user_input.lower() for word in ["해치", "위험", "위협"]):
                implications.append("potential_harm")
            if any(word in user_input.lower() for word in ["도움", "이익", "혜택"]):
                implications.append("potential_benefit")
            
            return implications
            
        except Exception as e:
            print(f"⚠️ 윤리적 함의 분석 중 오류: {str(e)}")
            return []

    def _analyze_consciousness(self, user_input: str, response: str) -> Dict:
        """의식 분석"""
        try:
            consciousness = {
                "self_awareness": False,
                "emotional_state": "neutral",
                "cognitive_load": 0.0
            }
            
            # 자기 인식 검사
            if any(word in user_input.lower() for word in ["나", "저", "내가"]):
                consciousness["self_awareness"] = True
            
            # 감정 상태 분석
            if any(word in user_input.lower() for word in ["행복", "기쁨", "좋아"]):
                consciousness["emotional_state"] = "positive"
            elif any(word in user_input.lower() for word in ["슬픔", "화남", "걱정"]):
                consciousness["emotional_state"] = "negative"
            
            # 인지 부하 계산
            words = user_input.split()
            consciousness["cognitive_load"] = min(len(words) / 20, 1.0)
            
            return consciousness
            
        except Exception as e:
            print(f"⚠️ 의식 분석 중 오류: {str(e)}")
            return {}

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()