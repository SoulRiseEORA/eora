# memory_core.py - 회상 메모리 저장소

from datetime import datetime
from typing import Dict, List, Optional
import json
import uuid
from pathlib import Path

class MemoryCore:
    def __init__(self):
        self.memories = []
        self.memory_manager = None
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }
        
        # 메모리 저장 경로
        self.memory_file = "memory_trace.json"
        self.backup_file = "memory_backup.json"
        
        # 메모리 설정
        self.max_memories = 10000
        self.auto_save_interval = 100  # 100개마다 자동 저장
        
        # 메모리 로드
        self._load_memories()

    def _load_memories(self) -> None:
        """저장된 메모리 로드"""
        try:
            if Path(self.memory_file).exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memories = data.get("memories", [])
                    print(f"✅ {len(self.memories)}개의 메모리 로드 완료")
            else:
                self.memories = []
                print("✅ 새로운 메모리 저장소 생성")
        except Exception as e:
            print(f"⚠️ 메모리 로드 실패: {str(e)}")
            self.memories = []

    def _save_memories(self) -> None:
        """메모리 저장"""
        try:
            # 백업 생성
            if Path(self.memory_file).exists():
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    json.dump({"memories": self.memories}, f, ensure_ascii=False, indent=2)
            
            # 메모리 저장
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({"memories": self.memories}, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 메모리 저장 실패: {str(e)}")

    def connect_memory_manager(self, memory_manager) -> bool:
        """메모리 관리자를 연결합니다."""
        try:
            self.memory_manager = memory_manager
            self.state["active"] = True
            self.state["last_update"] = datetime.utcnow().isoformat()
            print("✅ 메모리 관리자 연결 완료")
            return True
        except Exception as e:
            print(f"⚠️ 메모리 관리자 연결 실패: {str(e)}")
            return False

    async def process_memory(self, memory_atom: Dict) -> Dict:
        """메모리를 처리합니다."""
        try:
            if not self.state["active"]:
                return memory_atom

            # 1. 메모리 원자에 메타데이터 추가
            processed_atom = memory_atom.copy()
            processed_atom["memory_id"] = str(uuid.uuid4())
            processed_atom["processed_at"] = datetime.utcnow().isoformat()
            
            # 2. 메모리 저장
            self.memories.append(processed_atom)
            
            # 3. 메모리 크기 제한
            if len(self.memories) > self.max_memories:
                self.memories = self.memories[-self.max_memories:]
            
            # 4. 자동 저장
            if len(self.memories) % self.auto_save_interval == 0:
                self._save_memories()
            
            # 5. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return processed_atom
            
        except Exception as e:
            print(f"⚠️ 메모리 처리 중 오류: {str(e)}")
            return memory_atom

    async def recall_memory(self, query: str = None, limit: int = 10, 
                          memory_type: str = None, time_range: Dict = None) -> List[Dict]:
        """메모리 회상 - 향상된 검색 기능"""
        try:
            if not self.memories:
                return []
            
            # 1. 기본 필터링
            filtered_memories = self.memories.copy()
            
            # 2. 쿼리 기반 검색
            if query:
                query_lower = query.lower()
                filtered_memories = [
                    memory for memory in filtered_memories
                    if (query_lower in memory.get("user_input", "").lower() or
                        query_lower in str(memory.get("response", "")).lower())
                ]
            
            # 3. 메모리 타입 필터링
            if memory_type:
                filtered_memories = [
                    memory for memory in filtered_memories
                    if memory.get("response", {}).get("response_type") == memory_type
                ]
            
            # 4. 시간 범위 필터링
            if time_range:
                start_time = time_range.get("start")
                end_time = time_range.get("end")
                
                if start_time or end_time:
                    filtered_memories = [
                        memory for memory in filtered_memories
                        if self._is_in_time_range(memory.get("timestamp"), start_time, end_time)
                    ]
            
            # 5. 정렬 및 제한
            filtered_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return filtered_memories[:limit]
            
        except Exception as e:
            print(f"⚠️ 메모리 회상 중 오류: {str(e)}")
            return []

    def _is_in_time_range(self, timestamp: str, start_time: str = None, end_time: str = None) -> bool:
        """시간 범위 내에 있는지 확인"""
        try:
            if not timestamp:
                return False
                
            memory_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                if memory_time < start_dt:
                    return False
            
            if end_time:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                if memory_time > end_dt:
                    return False
            
            return True
            
        except Exception:
            return False

    async def search_memories_by_emotion(self, emotion: str, limit: int = 10) -> List[Dict]:
        """감정 기반 메모리 검색"""
        try:
            relevant_memories = []
            
            for memory in self.memories:
                response = memory.get("response", {})
                system_state = response.get("system_state", {})
                
                if system_state.get("emotion") == emotion:
                    relevant_memories.append(memory)
            
            relevant_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return relevant_memories[:limit]
            
        except Exception as e:
            print(f"⚠️ 감정 기반 메모리 검색 중 오류: {str(e)}")
            return []

    async def search_memories_by_resonance(self, min_resonance: float = 0.5, limit: int = 10) -> List[Dict]:
        """공명 점수 기반 메모리 검색"""
        try:
            relevant_memories = []
            
            for memory in self.memories:
                response = memory.get("response", {})
                analyses = response.get("analyses", {})
                wave_analysis = analyses.get("wave_analysis", {})
                
                resonance_score = wave_analysis.get("resonance_score", 0.0)
                if resonance_score >= min_resonance:
                    relevant_memories.append(memory)
            
            relevant_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return relevant_memories[:limit]
            
        except Exception as e:
            print(f"⚠️ 공명 기반 메모리 검색 중 오류: {str(e)}")
            return []

    def get_memory_statistics(self) -> Dict:
        """메모리 통계 정보"""
        try:
            if not self.memories:
                return {"total_memories": 0}
            
            # 기본 통계
            stats = {
                "total_memories": len(self.memories),
                "oldest_memory": self.memories[0].get("timestamp") if self.memories else None,
                "newest_memory": self.memories[-1].get("timestamp") if self.memories else None
            }
            
            # 응답 타입별 통계
            response_types = {}
            emotions = {}
            
            for memory in self.memories:
                response = memory.get("response", {})
                response_type = response.get("response_type", "unknown")
                emotion = response.get("system_state", {}).get("emotion", "unknown")
                
                response_types[response_type] = response_types.get(response_type, 0) + 1
                emotions[emotion] = emotions.get(emotion, 0) + 1
            
            stats["response_types"] = response_types
            stats["emotions"] = emotions
            
            return stats
            
        except Exception as e:
            print(f"⚠️ 메모리 통계 생성 중 오류: {str(e)}")
            return {"error": "통계 생성 실패"}

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()

    def store(self, input_text, response):
        """기존 호환성을 위한 메서드"""
        memory_atom = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": input_text,
            "response": response
        }
        self.memories.append(memory_atom)
        
        # 자동 저장
        if len(self.memories) % self.auto_save_interval == 0:
            self._save_memories()

    def recall_recent(self, n=3):
        """최근 메모리 조회"""
        return self.memories[-n:] if self.memories else []

    def clear(self):
        """메모리 초기화"""
        self.memories.clear()
        self._save_memories()
        print("✅ 메모리 초기화 완료")

    def count(self):
        """메모리 개수 반환"""
        return len(self.memories)

    def backup_memories(self) -> bool:
        """메모리 백업"""
        try:
            self._save_memories()
            print("✅ 메모리 백업 완료")
            return True
        except Exception as e:
            print(f"⚠️ 메모리 백업 실패: {str(e)}")
            return False
