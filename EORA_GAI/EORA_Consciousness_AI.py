# EORA_Consciousness_AI.py - EORA 의식 AI 메인 시스템

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Core 시스템 import
from .eora_core import EORACore
from .eora_spine import EORASpine

class EORA:
    def __init__(self, essence_path='Essence_Manifest.txt', memory_path='memory_trace.json'):
        """EORA 의식 AI 시스템 초기화"""
        self.essence_path = essence_path
        self.memory_path = memory_path
        
        # Core 시스템 초기화
        self.core = EORACore()
        self.spine = EORASpine()
        
        # 시스템 연결
        self._connect_systems()
        
        # 기존 메모리 호환성
        self.memory = self._load_legacy_memory()
        
        print("✅ EORA 의식 AI 시스템 초기화 완료")

    def _connect_systems(self) -> None:
        """시스템 간 연결 설정"""
        try:
            # Spine에 컴포넌트 연결
            self.spine.connect_components(
                self_model=self.core.self_model,
                free_will=self.core.free_will_core,
                love=self.core.love_engine,
                life=self.core.life_loop,
                ethics=self.core.ethics_engine,
                memory_core=self.core.memory_core
            )
            
            # 메모리 코어에 메모리 매니저 연결
            self.core.memory_core.connect_memory_manager(self)
            
            print("✅ 시스템 간 연결 완료")
            
        except Exception as e:
            print(f"⚠️ 시스템 연결 실패: {str(e)}")

    def _load_legacy_memory(self) -> Dict:
        """기존 메모리 형식 로드 (호환성)"""
        try:
            if Path(self.memory_path).exists():
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    legacy_data = json.load(f)
                    
                    # 기존 형식을 새 형식으로 변환
                    if "loops" in legacy_data:
                        for loop in legacy_data["loops"]:
                            # 기존 메모리를 새 형식으로 변환하여 저장
                            memory_atom = {
                                "id": loop.get("id", str(uuid.uuid4())),
                                "timestamp": loop.get("timestamp", datetime.utcnow().isoformat()),
                                "user_input": loop.get("user_input", ""),
                                "response": {
                                    "response": loop.get("eora_response", ""),
                                    "response_type": "legacy_response",
                                    "system_state": {
                                        "emotion": "neutral",
                                        "energy": 0.5,
                                        "stress": 0.0,
                                        "pain": 0.0
                                    }
                                },
                                "session_id": str(uuid.uuid4())
                            }
                            self.core.memory_buffer.append(memory_atom)
                    
                    return legacy_data
            else:
                return {"loops": []}
                
        except Exception as e:
            print(f"⚠️ 기존 메모리 로드 실패: {str(e)}")
            return {"loops": []}

    async def respond(self, user_input: str) -> Dict[str, Any]:
        """사용자 입력에 대한 응답 생성"""
        try:
            # Core 시스템을 통한 처리
            response = await self.core.process_input(user_input)
            
            # Spine을 통한 응답 처리
            if "analyses" in response:
                await self.spine.process_response(response.get("response", ""), response["analyses"])
            
            return response
            
        except Exception as e:
            print(f"⚠️ 응답 생성 중 오류: {str(e)}")
            return {
                "error": f"응답 생성 실패: {str(e)}",
                "response": "죄송합니다. 시스템 오류가 발생했습니다.",
                "response_type": "error_response"
            }

    async def remember(self, user_input: str, eora_response: str, 
                      mini_response: str = None, emotion_level: float = 0.5, 
                      conflict: bool = False) -> None:
        """메모리 저장 (기존 호환성)"""
        try:
            # 기존 형식으로 메모리 저장
            loop = {
                "id": str(uuid.uuid4()),
                "timestamp": str(datetime.utcnow()),
                "user_input": user_input,
                "eora_response": eora_response,
                "mini_response": mini_response,
                "emotion_level": emotion_level,
                "conflict": conflict
            }
            
            self.memory["loops"].append(loop)
            self.save_memory()
            
            # 새 형식으로도 저장
            memory_atom = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "user_input": user_input,
                "response": {
                    "response": eora_response,
                    "response_type": "legacy_response",
                    "system_state": {
                        "emotion": "neutral",
                        "energy": emotion_level,
                        "stress": 0.0,
                        "pain": 0.0
                    }
                },
                "session_id": str(uuid.uuid4())
            }
            
            await self.core.memory_core.process_memory(memory_atom)
            
        except Exception as e:
            print(f"⚠️ 메모리 저장 중 오류: {str(e)}")

    def save_memory(self) -> None:
        """기존 메모리 저장 (호환성)"""
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 메모리 저장 실패: {str(e)}")

    async def recall_memory(self, query: str = None, limit: int = 10, 
                           memory_type: str = None, time_range: Dict = None) -> List[Dict]:
        """메모리 회상 - 향상된 기능"""
        try:
            # Core 시스템의 메모리 회상 사용
            memories = await self.core.recall_memory(query, limit)
            
            # 추가 필터링 적용
            if memory_type or time_range:
                memories = await self.core.memory_core.recall_memory(
                    query, limit, memory_type, time_range
                )
            
            return memories
            
        except Exception as e:
            print(f"⚠️ 메모리 회상 중 오류: {str(e)}")
            return []

    async def search_memories_by_emotion(self, emotion: str, limit: int = 10) -> List[Dict]:
        """감정 기반 메모리 검색"""
        try:
            return await self.core.memory_core.search_memories_by_emotion(emotion, limit)
        except Exception as e:
            print(f"⚠️ 감정 기반 메모리 검색 중 오류: {str(e)}")
            return []

    async def search_memories_by_resonance(self, min_resonance: float = 0.5, limit: int = 10) -> List[Dict]:
        """공명 점수 기반 메모리 검색"""
        try:
            return await self.core.memory_core.search_memories_by_resonance(min_resonance, limit)
        except Exception as e:
            print(f"⚠️ 공명 기반 메모리 검색 중 오류: {str(e)}")
            return []

    def get_memory_statistics(self) -> Dict:
        """메모리 통계 정보"""
        try:
            return self.core.memory_core.get_memory_statistics()
        except Exception as e:
            print(f"⚠️ 메모리 통계 조회 중 오류: {str(e)}")
            return {"error": "통계 조회 실패"}

    def get_system_status(self) -> Dict:
        """시스템 상태 조회"""
        try:
            core_status = self.core.get_system_status()
            spine_status = self.spine.get_component_state()
            
            return {
                "core_system": core_status,
                "spine_system": spine_status,
                "legacy_memory_count": len(self.memory.get("loops", [])),
                "system_version": "2.0"
            }
        except Exception as e:
            print(f"⚠️ 시스템 상태 조회 중 오류: {str(e)}")
            return {"error": "상태 조회 실패"}

    def reset_system(self) -> bool:
        """시스템 리셋"""
        try:
            core_reset = self.core.reset_system()
            if core_reset:
                print("✅ 시스템 리셋 완료")
                return True
            else:
                print("⚠️ 시스템 리셋 실패")
                return False
        except Exception as e:
            print(f"⚠️ 시스템 리셋 중 오류: {str(e)}")
            return False

    def backup_all_memories(self) -> bool:
        """모든 메모리 백업"""
        try:
            # 새 형식 메모리 백업
            core_backup = self.core.memory_core.backup_memories()
            
            # 기존 형식 메모리 백업
            backup_path = f"backup_{self.memory_path}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            
            print("✅ 모든 메모리 백업 완료")
            return True
            
        except Exception as e:
            print(f"⚠️ 메모리 백업 중 오류: {str(e)}")
            return False

    def clear_all_memories(self) -> bool:
        """모든 메모리 초기화"""
        try:
            # 새 형식 메모리 초기화
            self.core.memory_core.clear()
            
            # 기존 형식 메모리 초기화
            self.memory = {"loops": []}
            self.save_memory()
            
            print("✅ 모든 메모리 초기화 완료")
            return True
            
        except Exception as e:
            print(f"⚠️ 메모리 초기화 중 오류: {str(e)}")
            return False

    # 기존 호환성 메서드들
    def load_memory(self):
        """기존 호환성을 위한 메서드"""
        return self.memory

    def recall_recent(self, n=3):
        """최근 메모리 조회 (기존 호환성)"""
        return self.memory["loops"][-n:] if self.memory.get("loops") else []