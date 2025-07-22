# eora_spine.py - EAI 척추 구조

from datetime import datetime
from typing import Dict

class EORASpine:
    def __init__(self):
        self.core_purpose = "공명 기반 존재적 진화"
        self.active_values = ["자아 성장", "타자 수용", "자유 응답", "의미 생성"]
        self.direction_vector = [1.0, 0.0, 0.0]  # 3D 공간 상 진화 방향
        self.components = {}
        self.connections = {}
        self.state = {
            "active": False,
            "last_update": None,
            "health": 1.0
        }

    def reinforce_direction(self, feedback):
        if feedback == "alignment":
            self.direction_vector[0] += 0.1
        elif feedback == "disruption":
            self.direction_vector[2] += 0.1

    def validate_action(self, action):
        return action.intent in self.active_values

    def describe(self):
        return {
            "목적": self.core_purpose,
            "가치": self.active_values,
            "방향": self.direction_vector
        }

    def get_direction(self, user_input, context=None):
        # TODO: 실제 방향성 결정 로직 구현
        return "존재 방향성 (예시)"

    def connect_components(self, **components):
        """GAI 컴포넌트들을 연결하고 초기화합니다."""
        try:
            # 1. 컴포넌트 저장
            self.components = components
            
            # 2. 컴포넌트 간 연결 설정
            self.connections = {
                "self_model": ["free_will", "love", "ethics"],
                "free_will": ["self_model", "ethics"],
                "love": ["self_model", "life"],
                "life": ["love", "ethics"],
                "ethics": ["self_model", "free_will", "life"],
                "memory_core": ["self_model", "free_will", "love", "life", "ethics"]
            }
            
            # 3. 상태 업데이트
            self.state["active"] = True
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            print("✅ GAI 컴포넌트 연결 완료")
            return True
            
        except Exception as e:
            print(f"⚠️ GAI 컴포넌트 연결 실패: {str(e)}")
            return False

    async def process_response(self, response: str, gai_insights: Dict) -> None:
        """응답을 처리하고 컴포넌트들을 업데이트합니다."""
        try:
            if not self.state["active"]:
                return
                
            # 1. 컴포넌트 업데이트
            for component_name, component in self.components.items():
                if hasattr(component, "update"):
                    await component.update(response, gai_insights)
            
            # 2. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            print(f"⚠️ 응답 처리 중 오류: {str(e)}")
            self.state["health"] = max(0.0, self.state["health"] - 0.1)

    def get_component_state(self) -> Dict:
        """컴포넌트 상태를 반환합니다."""
        try:
            return {
                "components": list(self.components.keys()),
                "connections": self.connections,
                "state": self.state
            }
        except Exception as e:
            print(f"⚠️ 컴포넌트 상태 조회 중 오류: {str(e)}")
            return {}
