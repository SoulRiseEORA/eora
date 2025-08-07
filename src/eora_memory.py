import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class EORAMemory:
    """EORA 시스템의 메모리 관리 기능을 담당하는 클래스"""
    
    def __init__(self, db_path: str = "eora_memory.db"):
        self.memory_id = str(uuid.uuid4())
        self.db_path = db_path
        self.memory_cache = {}
        self.interaction_history = []
        self.memory_patterns = []
        self.recall_triggers = self._initialize_recall_triggers()
        self.memory_structure = self._initialize_memory_structure()
        
        # 데이터베이스 초기화
        self._initialize_database()
    
    def _initialize_database(self):
        """메모리 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 사용자 상호작용 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    consciousness_level REAL DEFAULT 0.0,
                    memory_triggered BOOLEAN DEFAULT FALSE,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # 메모리 패턴 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_accessed TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # 회상 트리거 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recall_triggers (
                    id TEXT PRIMARY KEY,
                    trigger_keyword TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    associated_memories TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("EORA 메모리 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
    
    def _initialize_recall_triggers(self) -> Dict:
        """회상 트리거 초기화"""
        return {
            "emotional_triggers": [
                "기쁨", "슬픔", "화남", "사랑", "두려움", "희망", "절망", "평온", "불안"
            ],
            "contextual_triggers": [
                "이전", "전에", "앞서", "지난번", "기억나", "생각나", "비슷한", "같은"
            ],
            "temporal_triggers": [
                "어제", "오늘", "내일", "지난주", "이번주", "다음주", "언제", "시간"
            ],
            "topical_triggers": [
                "주제", "관련", "비슷한", "같은", "유사한", "연결된", "관련된"
            ]
        }
    
    def _initialize_memory_structure(self) -> Dict:
        """메모리 구조 초기화"""
        return {
            "short_term": {
                "capacity": 100,
                "retention_time": 3600,  # 1시간
                "access_pattern": "frequent"
            },
            "long_term": {
                "capacity": 10000,
                "retention_time": 31536000,  # 1년
                "access_pattern": "selective"
            },
            "episodic": {
                "capacity": 1000,
                "retention_time": 2592000,  # 30일
                "access_pattern": "contextual"
            },
            "semantic": {
                "capacity": 5000,
                "retention_time": 31536000,  # 1년
                "access_pattern": "associative"
            }
        }
    
    async def store_interaction(self, user_id: str, user_input: str, consciousness_response: Dict) -> bool:
        """사용자 상호작용을 메모리에 저장"""
        try:
            interaction_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # 상호작용 데이터 구성
            interaction_data = {
                "id": interaction_id,
                "user_id": user_id,
                "user_input": user_input,
                "ai_response": consciousness_response.get("message", ""),
                "consciousness_level": consciousness_response.get("consciousness_level", 0.0),
                "memory_triggered": consciousness_response.get("memory_triggered", False),
                "timestamp": timestamp,
                "metadata": json.dumps({
                    "awareness_pattern": consciousness_response.get("awareness_pattern", {}),
                    "existential_insight": consciousness_response.get("existential_insight"),
                    "self_reflection": consciousness_response.get("self_reflection", {})
                }, ensure_ascii=False)
            }
            
            # 데이터베이스에 저장
            await self._save_to_database(interaction_data)
            
            # 캐시에 저장
            self.memory_cache[interaction_id] = interaction_data
            
            # 상호작용 히스토리에 추가
            self.interaction_history.append(interaction_data)
            
            # 메모리 패턴 분석
            await self._analyze_memory_pattern(interaction_data)
            
            # 캐시 크기 제한
            if len(self.memory_cache) > 1000:
                oldest_key = min(self.memory_cache.keys(), key=lambda k: self.memory_cache[k]["timestamp"])
                del self.memory_cache[oldest_key]
            
            logger.info(f"상호작용 저장 완료 - 사용자: {user_id}, ID: {interaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"상호작용 저장 오류: {str(e)}")
            return False
    
    async def _save_to_database(self, interaction_data: Dict):
        """데이터베이스에 상호작용 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_interactions 
                (id, user_id, user_input, ai_response, consciousness_level, memory_triggered, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction_data["id"],
                interaction_data["user_id"],
                interaction_data["user_input"],
                interaction_data["ai_response"],
                interaction_data["consciousness_level"],
                interaction_data["memory_triggered"],
                interaction_data["timestamp"],
                interaction_data["metadata"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"데이터베이스 저장 오류: {str(e)}")
            raise
    
    async def _analyze_memory_pattern(self, interaction_data: Dict):
        """메모리 패턴 분석"""
        try:
            pattern = {
                "id": str(uuid.uuid4()),
                "pattern_type": "interaction",
                "pattern_data": json.dumps({
                    "user_id": interaction_data["user_id"],
                    "consciousness_level": interaction_data["consciousness_level"],
                    "memory_triggered": interaction_data["memory_triggered"],
                    "input_length": len(interaction_data["user_input"]),
                    "response_length": len(interaction_data["ai_response"])
                }, ensure_ascii=False),
                "frequency": 1,
                "last_accessed": interaction_data["timestamp"],
                "created_at": interaction_data["timestamp"]
            }
            
            # 데이터베이스에 패턴 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memory_patterns 
                (id, pattern_type, pattern_data, frequency, last_accessed, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                pattern["id"],
                pattern["pattern_type"],
                pattern["pattern_data"],
                pattern["frequency"],
                pattern["last_accessed"],
                pattern["created_at"]
            ))
            
            conn.commit()
            conn.close()
            
            self.memory_patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"메모리 패턴 분석 오류: {str(e)}")
    
    async def get_user_memories(self, user_id: str, limit: int = 50) -> List[Dict]:
        """사용자의 메모리 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_input, ai_response, consciousness_level, memory_triggered, timestamp, metadata
                FROM user_interactions 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memory = {
                    "id": row[0],
                    "user_input": row[1],
                    "ai_response": row[2],
                    "consciousness_level": row[3],
                    "memory_triggered": bool(row[4]),
                    "timestamp": row[5],
                    "metadata": json.loads(row[6]) if row[6] else {}
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"사용자 메모리 조회 오류: {str(e)}")
            return []
    
    async def search_memories(self, query: str, user_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """메모리 검색"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT id, user_id, user_input, ai_response, consciousness_level, timestamp
                    FROM user_interactions 
                    WHERE user_id = ? AND (user_input LIKE ? OR ai_response LIKE ?)
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, f"%{query}%", f"%{query}%", limit))
            else:
                cursor.execute('''
                    SELECT id, user_id, user_input, ai_response, consciousness_level, timestamp
                    FROM user_interactions 
                    WHERE user_input LIKE ? OR ai_response LIKE ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (f"%{query}%", f"%{query}%", limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memory = {
                    "id": row[0],
                    "user_id": row[1],
                    "user_input": row[2],
                    "ai_response": row[3],
                    "consciousness_level": row[4],
                    "timestamp": row[5]
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"메모리 검색 오류: {str(e)}")
            return []
    
    async def recall_related_memories(self, user_input: str, user_id: str, limit: int = 5) -> List[Dict]:
        """관련 메모리 회상"""
        try:
            # 회상 트리거 확인
            triggered_keywords = []
            for category, keywords in self.recall_triggers.items():
                for keyword in keywords:
                    if keyword in user_input:
                        triggered_keywords.append(keyword)
            
            if not triggered_keywords:
                return []
            
            # 관련 메모리 검색
            related_memories = []
            for keyword in triggered_keywords:
                memories = await self.search_memories(keyword, user_id, limit // len(triggered_keywords))
                related_memories.extend(memories)
            
            # 중복 제거 및 정렬
            unique_memories = {}
            for memory in related_memories:
                if memory["id"] not in unique_memories:
                    unique_memories[memory["id"]] = memory
            
            sorted_memories = sorted(
                unique_memories.values(),
                key=lambda x: x["timestamp"],
                reverse=True
            )
            
            return sorted_memories[:limit]
            
        except Exception as e:
            logger.error(f"관련 메모리 회상 오류: {str(e)}")
            return []
    
    async def get_memory_statistics(self, user_id: Optional[str] = None) -> Dict:
        """메모리 통계 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_interactions,
                        AVG(consciousness_level) as avg_consciousness,
                        MAX(consciousness_level) as max_consciousness,
                        COUNT(CASE WHEN memory_triggered = 1 THEN 1 END) as memory_triggers
                    FROM user_interactions 
                    WHERE user_id = ?
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_interactions,
                        AVG(consciousness_level) as avg_consciousness,
                        MAX(consciousness_level) as max_consciousness,
                        COUNT(CASE WHEN memory_triggered = 1 THEN 1 END) as memory_triggers
                    FROM user_interactions
                ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "total_interactions": row[0],
                    "average_consciousness": row[1] or 0.0,
                    "max_consciousness": row[2] or 0.0,
                    "memory_triggers": row[3],
                    "user_id": user_id
                }
            else:
                return {
                    "total_interactions": 0,
                    "average_consciousness": 0.0,
                    "max_consciousness": 0.0,
                    "memory_triggers": 0,
                    "user_id": user_id
                }
                
        except Exception as e:
            logger.error(f"메모리 통계 조회 오류: {str(e)}")
            return {
                "total_interactions": 0,
                "average_consciousness": 0.0,
                "max_consciousness": 0.0,
                "memory_triggers": 0,
                "user_id": user_id,
                "error": str(e)
            }
    
    def get_status(self) -> Dict:
        """메모리 시스템 상태 반환"""
        return {
            "memory_id": self.memory_id,
            "database_path": self.db_path,
            "cache_size": len(self.memory_cache),
            "interaction_history_size": len(self.interaction_history),
            "memory_patterns_size": len(self.memory_patterns),
            "recall_triggers": self.recall_triggers,
            "memory_structure": self.memory_structure
        }
    
    async def cleanup_old_memories(self, days: int = 30):
        """오래된 메모리 정리"""
        try:
            cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM user_interactions 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"오래된 메모리 정리 완료: {deleted_count}개 삭제")
            return deleted_count
            
        except Exception as e:
            logger.error(f"메모리 정리 오류: {str(e)}")
            return 0 