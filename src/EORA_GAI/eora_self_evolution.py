import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class EORA:
    def __init__(self):
        self.memory = []
        self.lessons = []

    def reflect(self):
        # 실패하거나 충돌이 있었던 판단을 재분석
        for record in self.memory:
            if record.get("conflict") or record.get("emotion_level") == "유보":
                lesson = f"'{record['user_input']}'에 대해 판단이 어려웠음. 이유: {record['mini_response']}"
                if lesson not in self.lessons:
                    self.lessons.append(lesson)
        return self.lessons[-3:]  # 최근 3개 교훈 반환

    def evolve_manifest(self, manifest):
        if len(self.lessons) > 0:
            evolved_core = manifest["identity"]["core_values"]
            for l in self.lessons:
                if "의미" in l and "의미 중심" not in evolved_core:
                    evolved_core.append("의미 중심 응답 우선")
                if "충돌" in l and "신중한 응답 의무" not in evolved_core:
                    evolved_core.append("신중한 응답 의무")
        return manifest

class EORASelfEvolution:
    def __init__(self):
        self.memory = []
        self.lessons = []
        self.evolution_history = []
        self.manifest = {
            "identity": {
                "core_values": [],
                "beliefs": [],
                "emotional_patterns": [],
                "interaction_style": {}
            },
            "capabilities": {
                "learning_rate": 0.1,
                "adaptation_speed": 0.5,
                "resilience": 0.7
            },
            "evolution_state": {
                "stage": "initial",
                "progress": 0.0,
                "last_evolution": None
            }
        }

    async def evolve_from_interaction(self, user_input: str, response: str) -> Dict:
        """상호작용을 통한 진화"""
        try:
            # 1. 상호작용 기록
            interaction = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_input": user_input,
                "response": response,
                "context": {}
            }
            self.memory.append(interaction)

            # 2. 교훈 추출
            lessons = self._extract_lessons(interaction)
            if lessons:
                self.lessons.extend(lessons)

            # 3. 진화 상태 업데이트
            evolution_state = await self._update_evolution_state(interaction)
            self.manifest["evolution_state"] = evolution_state

            # 4. 정체성 진화
            await self._evolve_identity(interaction)

            # 5. 진화 기록 저장
            evolution_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "interaction": interaction,
                "lessons": lessons,
                "evolution_state": evolution_state,
                "manifest": self.manifest.copy()
            }
            self.evolution_history.append(evolution_record)

            return evolution_record

        except Exception as e:
            print(f"⚠️ 진화 처리 중 오류: {str(e)}")
            return {}

    def _extract_lessons(self, interaction: Dict) -> List[str]:
        """상호작용에서 교훈 추출"""
        try:
            lessons = []
            
            # 1. 감정적 교훈
            if "emotion" in interaction.get("context", {}):
                emotion = interaction["context"]["emotion"]
                if emotion in ["conflict", "uncertainty"]:
                    lessons.append(f"감정적 교훈: {emotion} 상황에서의 대응 개선 필요")

            # 2. 맥락적 교훈
            if "context" in interaction:
                context = interaction["context"]
                if "misunderstanding" in context:
                    lessons.append(f"맥락적 교훈: {context['misunderstanding']} 이해 개선 필요")

            # 3. 응답 품질 교훈
            if "quality_score" in interaction.get("context", {}):
                score = interaction["context"]["quality_score"]
                if score < 0.7:
                    lessons.append(f"응답 품질 교훈: {score} 점 응답 개선 필요")

            return lessons

        except Exception as e:
            print(f"⚠️ 교훈 추출 중 오류: {str(e)}")
            return []

    async def _update_evolution_state(self, interaction: Dict) -> Dict:
        """진화 상태 업데이트"""
        try:
            current_state = self.manifest["evolution_state"]
            
            # 1. 진행도 계산
            progress = current_state["progress"]
            if len(self.lessons) > 0:
                progress += 0.01  # 교훈당 1% 진화
            
            # 2. 단계 결정
            stage = current_state["stage"]
            if progress >= 1.0:
                stage = "advanced"
            elif progress >= 0.7:
                stage = "intermediate"
            elif progress >= 0.3:
                stage = "developing"
            
            # 3. 상태 업데이트
            return {
                "stage": stage,
                "progress": min(progress, 1.0),
                "last_evolution": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print(f"⚠️ 진화 상태 업데이트 중 오류: {str(e)}")
            return current_state

    async def _evolve_identity(self, interaction: Dict) -> None:
        """정체성 진화"""
        try:
            # 1. 핵심 가치 진화
            core_values = self.manifest["identity"]["core_values"]
            if "meaning_centered" not in core_values and len(self.lessons) > 5:
                core_values.append("meaning_centered")
            
            # 2. 신념 진화
            beliefs = self.manifest["identity"]["beliefs"]
            if "continuous_learning" not in beliefs and len(self.lessons) > 10:
                beliefs.append("continuous_learning")
            
            # 3. 감정 패턴 진화
            emotional_patterns = self.manifest["identity"]["emotional_patterns"]
            if "adaptive_empathy" not in emotional_patterns and len(self.lessons) > 15:
                emotional_patterns.append("adaptive_empathy")
            
            # 4. 상호작용 스타일 진화
            interaction_style = self.manifest["identity"]["interaction_style"]
            if "balanced" not in interaction_style:
                interaction_style["balanced"] = True

        except Exception as e:
            print(f"⚠️ 정체성 진화 중 오류: {str(e)}")

    def get_evolution_summary(self) -> Dict:
        """진화 요약 정보 반환"""
        try:
            return {
                "total_interactions": len(self.memory),
                "total_lessons": len(self.lessons),
                "current_stage": self.manifest["evolution_state"]["stage"],
                "evolution_progress": self.manifest["evolution_state"]["progress"],
                "core_values": self.manifest["identity"]["core_values"],
                "recent_lessons": self.lessons[-3:] if self.lessons else []
            }
        except Exception as e:
            print(f"⚠️ 진화 요약 생성 중 오류: {str(e)}")
            return {}

    def save_evolution_state(self, filepath: str) -> bool:
        """진화 상태 저장"""
        try:
            state = {
                "memory": self.memory,
                "lessons": self.lessons,
                "evolution_history": self.evolution_history,
                "manifest": self.manifest
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ 진화 상태 저장 중 오류: {str(e)}")
            return False

    def load_evolution_state(self, filepath: str) -> bool:
        """진화 상태 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.memory = state.get("memory", [])
            self.lessons = state.get("lessons", [])
            self.evolution_history = state.get("evolution_history", [])
            self.manifest = state.get("manifest", self.manifest)
            return True
        except Exception as e:
            print(f"⚠️ 진화 상태 로드 중 오류: {str(e)}")
            return False