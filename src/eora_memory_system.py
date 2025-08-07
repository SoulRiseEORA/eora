"""
EORA 완전 통합 메모리 시스템
- 저장: 감정, 신념, 맥락, 연결을 포함한 다차원 메모리 저장
- 회상: 감정 기반, 맥락 기반, 연결 기반 다중 회상 전략
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from bson import ObjectId
import re
import hashlib

logger = logging.getLogger(__name__)

class EORAMemorySystem:
    """완전 통합된 EORA 메모리 시스템"""
    
    def __init__(self, mongo_uri=None):
        # MongoDB 연결 설정 - database.py와 연결 정보 공유
        if mongo_uri is None:
            import os
            
            # 1순위: database.py에서 이미 연결된 클라이언트 또는 URL 사용
            try:
                import sys
                sys.path.append('.')
                from database import get_cached_mongodb_connection, get_mongodb_url, MONGODB_URL
                
                # 이미 연결된 클라이언트가 있으면 재사용
                cached_client = get_cached_mongodb_connection()
                if cached_client:
                    try:
                        cached_client.admin.command('ping')
                        logger.info("✅ database.py의 기존 MongoDB 연결 재사용")
                        self.client = cached_client
                        self.db = self.client["eora_memory"]
                        self._setup_collections()
                        self._create_indexes()
                        
                        # 메모리 설정 및 memory_manager 초기화
                        self.max_memories_per_user = 1000
                        self.recall_limit = 10
                        self.emotion_threshold = 0.3
                        self.connection_threshold = 0.5
                        self.memory_manager = None
                        self._initialize_memory_manager()
                        
                        return  # 성공적으로 연결 재사용
                    except:
                        logger.warning("⚠️ 기존 연결이 끊어져 있음, 새로 연결 시도")
                
                # 기존 연결이 없으면 URL 가져오기
                mongo_uri = get_mongodb_url()
                if mongo_uri and mongo_uri != "mongodb://localhost:27017":
                    logger.info(f"✅ database.py get_mongodb_url()에서 URL 가져옴: {mongo_uri[:50]}...")
                elif MONGODB_URL and MONGODB_URL != "mongodb://localhost:27017":
                    mongo_uri = MONGODB_URL
                    logger.info(f"✅ database.py MONGODB_URL에서 URL 가져옴: {mongo_uri[:50]}...")
                else:
                    mongo_uri = None
                    
            except (ImportError, Exception) as e:
                logger.warning(f"⚠️ database.py 가져오기 실패: {e}")
                mongo_uri = None
            
            # 2순위: 직접 환경변수에서 Railway MongoDB URL 찾기
            if not mongo_uri:
                is_railway = any([
                    os.getenv("RAILWAY_ENVIRONMENT"),
                    os.getenv("RAILWAY_PROJECT_ID"),
                    os.getenv("RAILWAY_SERVICE_ID")
                ])
                
                if is_railway:
                    # Railway 환경변수 확인 (포괄적)
                    railway_env_keys = [
                        "MONGODB_URL", "MONGO_URL", "MONGO_PUBLIC_URL", "MONGO_PRIVATE_URL",
                        "DATABASE_URL", "DB_URL", "MONGODB_URI", "MONGO_URI"
                    ]
                    
                    logger.info(f"🔍 Railway 환경에서 MongoDB URL 검색 중...")
                    
                    for key in railway_env_keys:
                        value = os.getenv(key)
                        if value and value.startswith("mongodb://"):
                            mongo_uri = value.strip()
                            logger.info(f"✅ 환경변수 {key}에서 MongoDB URL 발견: {mongo_uri[:50]}...")
                            break
                    
                    # 개별 변수로 구성 시도
                    if not mongo_uri and all([os.getenv('MONGOUSER'), os.getenv('MONGOPASSWORD'), 
                                            os.getenv('MONGOHOST'), os.getenv('MONGOPORT')]):
                        mongo_uri = f"mongodb://{os.getenv('MONGOUSER')}:{os.getenv('MONGOPASSWORD')}@{os.getenv('MONGOHOST')}:{os.getenv('MONGOPORT')}"
                        logger.info(f"✅ 개별 환경변수로 MongoDB URL 구성: {mongo_uri[:50]}...")
                
                # 로컬 환경이거나 Railway에서 URL을 못 찾은 경우
                if not mongo_uri:
                    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
                    if mongo_uri == "mongodb://localhost:27017":
                        logger.info(f"✅ 기본 localhost 사용: {mongo_uri}")
                    else:
                        logger.info(f"✅ MONGODB_URI 환경변수 사용: {mongo_uri[:50]}...")
        
        # 최종 fallback
        if not mongo_uri:
            mongo_uri = "mongodb://localhost:27017"
            logger.warning(f"⚠️ 최종 fallback - localhost 사용: {mongo_uri}")
        
        self.mongo_uri = mongo_uri
        self.client = None
        self.db = None
        self.memories = None
        
        # 이미 database.py 연결을 재사용한 경우가 아니라면 새로 연결
        if self.client is None:
            
            # MongoDB 연결 시도 (Railway 환경에 맞는 설정)
            try:
                # Railway 환경 감지
                import os
                is_railway = any([
                    os.getenv("RAILWAY_ENVIRONMENT"),
                    os.getenv("RAILWAY_PROJECT_ID"),
                    os.getenv("RAILWAY_SERVICE_ID")
                ])
                
                # Railway 환경에 맞는 연결 옵션 설정
                connect_options = {
                    "serverSelectionTimeoutMS": 10000,  # Railway에서는 더 긴 타임아웃
                    "connectTimeoutMS": 10000,
                    "socketTimeoutMS": 20000,
                }
                
                if is_railway:
                    connect_options.update({
                        "retryWrites": True,
                        "w": "majority",
                        "readPreference": "primary",
                        "maxPoolSize": 10,
                        "minPoolSize": 1
                    })
                
                self.client = MongoClient(mongo_uri, **connect_options)
                
                # 연결 테스트
                self.client.admin.command('ping')
                self.db = self.client["eora_memory"]
                
                # 컬렉션 설정
                self._setup_collections()
                
                logger.info(f"✅ MongoDB 연결 성공: {mongo_uri}")
                
                # 인덱스 생성
                self._create_indexes()
                
            except Exception as e:
                logger.error(f"❌ MongoDB 연결 실패: {str(e)}")
                logger.error(f"   URI: {mongo_uri}")
                # 연결 실패 시에도 객체는 생성하되, 컬렉션들을 None으로 설정
                self.client = None
                self.db = None
                self.memories = None
                self.emotion_memories = None
                self.belief_memories = None
                self.context_memories = None
                self.connection_index = None
            
        # 메모리 설정
        self.max_memories_per_user = 1000
        self.recall_limit = 10
        self.emotion_threshold = 0.3
        self.connection_threshold = 0.5
        
        # memory_manager 초기화 (RecallEngine과 호환성을 위해)
        self.memory_manager = None
        self._initialize_memory_manager()
    
    def _initialize_memory_manager(self):
        """memory_manager 초기화 (RecallEngine 호환성) - Railway 환경 대응"""
        try:
            # Railway 환경 확인
            import os
            is_railway = any([
                os.getenv("RAILWAY_ENVIRONMENT"),
                os.getenv("RAILWAY_PROJECT_ID"),
                os.getenv("RAILWAY_SERVICE_ID")
            ])
            
            if is_railway:
                logger.info("🚂 Railway 환경에서 memory_manager 초기화 시도...")
                
                # Railway에서는 경량화된 memory_manager 생성
                self.memory_manager = self._create_lightweight_memory_manager()
                
                if self.memory_manager:
                    logger.info("✅ Railway용 경량 memory_manager 생성 완료")
                else:
                    logger.warning("⚠️ Railway에서 memory_manager 생성 실패 - 기본 회상 사용")
            else:
                # 로컬 환경에서는 OpenAI API 오류 시 즉시 경량 버전 사용
                logger.info("💻 로컬 환경에서 memory_manager 초기화 시도...")
                
                # 항상 경량 버전 사용 (무한루프 방지)
                logger.info("⚡ 빠른 초기화를 위해 경량 memory_manager 사용")
                self.memory_manager = self._create_lightweight_memory_manager()
                
        except Exception as e:
            logger.warning(f"⚠️ memory_manager 초기화 실패: {e}")
            # 최종 fallback으로 경량 버전 생성
            self.memory_manager = self._create_lightweight_memory_manager()
    
    def _create_lightweight_memory_manager(self):
        """Railway 환경용 경량 memory_manager 생성"""
        try:
            # self 참조를 캡처하여 MongoDB에 접근
            eora_system = self
            
            class LightweightMemoryManager:
                def __init__(self):
                    self.is_initialized = True
                    self.memories = {}
                    
                async def store_memory_async(self, content, metadata=None):
                    """메모리 저장 (간단 버전)"""
                    memory_id = f"mem_{len(self.memories)}"
                    self.memories[memory_id] = {
                        "content": content,
                        "metadata": metadata or {},
                        "timestamp": datetime.now().isoformat()
                    }
                    return {"success": True, "memory_id": memory_id}
                
                async def recall_memories_async(self, query, limit=5):
                    """메모리 회상 (MongoDB 연동 버전)"""
                    results = []
                    query_lower = query.lower()
                    
                    try:
                        # MongoDB에서 실제 데이터 검색
                        if eora_system.is_connected():
                            # 텍스트 검색 조건
                            search_conditions = []
                            
                            # 전체 문서 검색
                            search_conditions.append({"content": {"$regex": query_lower, "$options": "i"}})
                            
                            # 단어별 검색
                            query_words = query_lower.split()
                            for word in query_words:
                                if len(word) > 2:
                                    search_conditions.append({"content": {"$regex": word, "$options": "i"}})
                            
                            if search_conditions:
                                mongodb_results = list(eora_system.memories.find({
                                    "$or": search_conditions
                                }).limit(limit * 2))  # 더 많이 가져와서 점수 계산 후 필터링
                                
                                # 점수 계산
                                scored_memories = []
                                for doc in mongodb_results:
                                    content = doc.get("content", "").lower()
                                    score = 0
                                    
                                    # 정확한 매칭
                                    if query_lower in content:
                                        score += 10
                                    
                                    # 단어별 매칭
                                    for word in query_words:
                                        if len(word) > 2 and word in content:
                                            score += 5
                                    
                                    if score > 0:
                                        result_data = {
                                            "content": doc.get("content", ""),
                                            "metadata": doc.get("metadata", {}),
                                            "timestamp": doc.get("timestamp"),
                                            "memory_id": str(doc.get("_id")),
                                            "score": score,
                                            "user_id": doc.get("user_id"),
                                            "memory_type": doc.get("memory_type")
                                        }
                                        scored_memories.append(result_data)
                                
                                # 점수순 정렬 후 상위 결과 반환
                                scored_memories.sort(key=lambda x: x["score"], reverse=True)
                                return scored_memories[:limit]
                    
                    except Exception as e:
                        logger.error(f"MongoDB 검색 오류: {e}")
                    
                    # MongoDB 실패 시 내부 메모리에서 검색 (fallback)
                    scored_memories = []
                    for mem_id, mem_data in self.memories.items():
                        content = mem_data["content"].lower()
                        score = 0
                        
                        if query_lower in content:
                            score += 10
                        
                        query_words = query_lower.split()
                        for word in query_words:
                            if len(word) > 2 and word in content:
                                score += 5
                        
                        if score > 0:
                            result_data = mem_data.copy()
                            result_data["score"] = score
                            result_data["memory_id"] = mem_id
                            scored_memories.append(result_data)
                    
                    scored_memories.sort(key=lambda x: x["score"], reverse=True)
                    return scored_memories[:limit]
            
            return LightweightMemoryManager()
            
        except Exception as e:
            logger.error(f"경량 memory_manager 생성 실패: {e}")
            return None
    
    def _setup_collections(self):
        """컬렉션 설정"""
        if self.db is not None:
            self.memories = self.db["memories"]
            self.emotion_memories = self.db["emotion_memories"]
            self.belief_memories = self.db["belief_memories"]
            self.context_memories = self.db["context_memories"]
            self.connection_index = self.db["connection_index"]
            logger.info("✅ 메모리 컬렉션 설정 완료")
    
    def is_connected(self):
        """MongoDB 연결 상태 확인"""
        try:
            if self.client is not None and self.db is not None and self.memories is not None:
                self.client.admin.command('ping')
                return True
            return False
        except Exception as e:
            logger.debug(f"연결 상태 확인 중 오류: {str(e)}")
            return False
        
    def _create_indexes(self):
        """데이터베이스 인덱스 생성"""
        try:
            # 기본 메모리 인덱스
            self.memories.create_index([("user_id", 1), ("timestamp", -1)])
            self.memories.create_index([("topic", 1), ("emotion_score", -1)])
            self.memories.create_index([("connections", 1)])
            
            # 감정 메모리 인덱스
            self.emotion_memories.create_index([("emotion_label", 1), ("timestamp", -1)])
            self.emotion_memories.create_index([("emotion_score", -1)])
            
            # 신념 메모리 인덱스
            self.belief_memories.create_index([("belief_tags", 1), ("timestamp", -1)])
            
            # 맥락 메모리 인덱스
            self.context_memories.create_index([("context_keywords", 1), ("timestamp", -1)])
            
            logger.info("메모리 시스템 인덱스 생성 완료")
        except Exception as e:
            logger.error(f"인덱스 생성 오류: {str(e)}")
    
    async def save_memory(self, 
                         user_id: str,
                         user_input: str, 
                         ai_response: str,
                         consciousness_level: float = 0.0,
                         emotion_data: Dict = None,
                         belief_data: Dict = None,
                         context_data: Dict = None,
                         session_id: str = None) -> Dict:
        """다차원 메모리 저장"""
        if not self.is_connected():
            logger.warning("MongoDB 연결이 없어 메모리 저장을 건너뜁니다")
            return {"success": False, "error": "no_connection"}
            
        try:
            timestamp = datetime.now()
            
            # 기본 메모리 데이터
            memory_data = {
                "user_id": user_id,
                "timestamp": timestamp,
                "session_id": session_id or f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                "user_input": user_input,
                "ai_response": ai_response,
                "consciousness_level": consciousness_level,
                "emotion_score": emotion_data.get("score", 0.0) if emotion_data else 0.0,
                "emotion_label": emotion_data.get("label", "neutral") if emotion_data else "neutral",
                "belief_tags": belief_data.get("tags", []) if belief_data else [],
                "context_keywords": context_data.get("keywords", []) if context_data else [],
                "topic": self._extract_topic(user_input),
                "sub_topic": self._extract_sub_topic(user_input),
                "summary": self._generate_summary(user_input, ai_response),
                "importance_score": self._calculate_importance(user_input, ai_response, consciousness_level),
                "connections": [],
                "last_accessed": None,
                "access_count": 0,
                "forgetting_score": 1.0
            }
            
            # 메모리 저장
            result = self.memories.insert_one(memory_data)
            memory_id = str(result.inserted_id)
            
            # 감정 메모리 저장
            if emotion_data and emotion_data.get("score", 0) > self.emotion_threshold:
                await self._save_emotion_memory(memory_id, emotion_data, timestamp)
            
            # 신념 메모리 저장
            if belief_data and belief_data.get("tags"):
                await self._save_belief_memory(memory_id, belief_data, timestamp)
            
            # 맥락 메모리 저장
            if context_data and context_data.get("keywords"):
                await self._save_context_memory(memory_id, context_data, timestamp)
            
            # 연결 관계 업데이트
            await self._update_connections(memory_id, user_input, ai_response)
            
            logger.info(f"메모리 저장 완료 - 사용자: {user_id}, ID: {memory_id}")
            return {"memory_id": memory_id, "status": "saved"}
            
        except Exception as e:
            logger.error(f"메모리 저장 오류: {str(e)}")
            return {"error": str(e)}
    
    async def store_memory(self, content: str, memory_type: str = "general", user_id: str = None, metadata: Dict = None) -> Dict:
        """
        메모리 저장 (학습된 파일 청크 전용)
        
        Args:
            content (str): 저장할 내용
            memory_type (str): 메모리 타입 (document_chunk, conversation, general 등)
            user_id (str): 사용자 ID
            metadata (Dict): 추가 메타데이터
            
        Returns:
            Dict: 저장 결과
        """
        try:
            # 입력 검증
            if not content or not isinstance(content, str):
                return {
                    "success": False,
                    "error": "내용이 비어있거나 문자열이 아닙니다",
                    "type": memory_type
                }
            
            # MongoDB 연결 확인
            if not self.is_connected():
                error_msg = "MongoDB 연결이 실패했습니다"
                if not self.client:
                    error_msg += " (클라이언트 없음)"
                elif self.db is None:
                    error_msg += " (데이터베이스 없음)"
                elif not self.memories:
                    error_msg += " (메모리 컬렉션 없음)"
                else:
                    error_msg += " (연결 테스트 실패)"
                
                logger.error(f"❌ {error_msg} - URI: {self.mongo_uri}")
                return {
                    "success": False,
                    "error": error_msg,
                    "type": memory_type,
                    "mongo_uri": self.mongo_uri
                }
            
            timestamp = datetime.now()
            metadata = metadata or {}
            
            # 기본 메모리 데이터 구성
            memory_data = {
                "user_id": user_id or "system",
                "timestamp": timestamp,
                "content": content,
                "memory_type": memory_type,
                "metadata": metadata,
                "source": metadata.get("source", "file_learning"),
                "filename": metadata.get("filename", "unknown"),
                "file_extension": metadata.get("file_extension", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "total_chunks": metadata.get("total_chunks", 1),
                "importance_score": self._calculate_content_importance(content),
                "topic": self._extract_topic(content),
                "keywords": self._extract_keywords(content),
                "last_accessed": None,
                "access_count": 0,
                "forgetting_score": 1.0,
                "created_at": timestamp.isoformat()
            }
            
            # MongoDB에 저장
            try:
                result = self.memories.insert_one(memory_data)
                memory_id = str(result.inserted_id)
                
                # 저장 검증: 실제로 저장되었는지 확인
                saved_doc = self.memories.find_one({"_id": result.inserted_id})
                if not saved_doc:
                    logger.error(f"❌ 저장 검증 실패: 문서가 실제로 저장되지 않음")
                    return {
                        "success": False,
                        "error": "저장 검증 실패: 문서가 데이터베이스에서 찾을 수 없음",
                        "type": memory_type
                    }
                
                logger.info(f"✅ MongoDB 저장 및 검증 완료 - ID: {memory_id}")
                
            except Exception as db_error:
                logger.error(f"❌ MongoDB 삽입 오류: {str(db_error)}")
                return {
                    "success": False,
                    "error": f"데이터베이스 저장 실패: {str(db_error)}",
                    "type": memory_type
                }
            
            # 파일 청크의 경우 추가 인덱싱
            if memory_type == "document_chunk":
                try:
                    self._index_document_chunk_sync(memory_id, content, metadata)
                except Exception as index_error:
                    logger.warning(f"⚠️ 인덱싱 오류 (저장은 성공): {str(index_error)}")
            
            logger.info(f"✅ 메모리 저장 완료 - ID: {memory_id}, 타입: {memory_type}, 내용: {content[:50]}...")
            
            return {
                "success": True,
                "memory_id": memory_id, 
                "status": "saved",
                "type": memory_type,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"❌ 메모리 저장 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "type": memory_type
            }
    
    def _calculate_content_importance(self, content: str) -> float:
        """내용의 중요도 계산"""
        try:
            # 기본 점수
            importance = 0.5
            
            # 내용 길이에 따른 가중치
            if len(content) > 500:
                importance += 0.2
            elif len(content) > 200:
                importance += 0.1
            
            # 특정 키워드 가중치
            important_keywords = ["중요", "핵심", "기본", "원리", "방법", "개념", "정의", "설명"]
            for keyword in important_keywords:
                if keyword in content:
                    importance += 0.1
                    break
            
            # 질문 형태인 경우 가중치
            if "?" in content or "무엇" in content or "어떻게" in content:
                importance += 0.1
            
            return min(importance, 1.0)
            
        except Exception:
            return 0.5
    
    def _extract_keywords(self, content: str) -> List[str]:
        """내용에서 키워드 추출"""
        try:
            # 간단한 키워드 추출 (실제로는 더 정교한 NLP 기법 사용 가능)
            words = re.findall(r'\b\w{2,}\b', content)
            # 빈도 기반 상위 키워드 추출
            from collections import Counter
            word_freq = Counter(words)
            return [word for word, freq in word_freq.most_common(10)]
        except Exception:
            return []
    
    def _index_document_chunk_sync(self, memory_id: str, content: str, metadata: Dict):
        """문서 청크 추가 인덱싱 (동기 버전)"""
        try:
            # 문서별 청크 인덱스 생성
            chunk_index = {
                "memory_id": memory_id,
                "filename": metadata.get("filename", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "content_hash": hashlib.md5(content.encode()).hexdigest(),
                "indexed_at": datetime.now(),
                "searchable_content": content.lower()  # 검색용
            }
            
            # 별도 컬렉션에 저장 (빠른 검색을 위해)
            if "document_chunks" not in self.db.list_collection_names():
                self.db.create_collection("document_chunks")
                self.db["document_chunks"].create_index([("filename", 1), ("chunk_index", 1)])
                self.db["document_chunks"].create_index([("searchable_content", "text")])
            
            self.db["document_chunks"].insert_one(chunk_index)
            logger.debug(f"문서 청크 인덱싱 완료: {memory_id}")
            
        except Exception as e:
            logger.error(f"문서 청크 인덱싱 오류: {str(e)}")
    
    async def recall_learned_content(self, query: str, memory_type: str = None, filename: str = None, limit: int = 5, user_id: str = None) -> List[Dict]:
        """
        학습된 내용 회상
        
        Args:
            query (str): 검색어
            memory_type (str): 메모리 타입 필터 (document_chunk, conversation 등)
            filename (str): 파일명 필터
            limit (int): 결과 제한
            user_id (str): 사용자 ID 필터
            
        Returns:
            List[Dict]: 회상된 메모리들
        """
        if not self.is_connected():
            logger.warning("MongoDB 연결이 없어 학습된 내용 회상을 건너뜁니다")
            return []
            
        try:
            # 기본 필터 조건들
            base_filters = []
            
            # 사용자 ID 필터 + 공유 데이터 포함
            if user_id:
                # 사용자 개인 데이터 + 관리자 공유 데이터 모두 검색
                user_filter = {
                    "$or": [
                        {"user_id": user_id},  # 개인 데이터
                        {"user_id": "admin_shared", "shared_to_all": True}  # 관리자 공유 데이터
                    ]
                }
                base_filters.append(user_filter)
            
            # 메모리 타입 필터
            if memory_type:
                base_filters.append({"memory_type": memory_type})
            
            # 파일명 필터
            if filename:
                base_filters.append({"filename": {"$regex": filename, "$options": "i"}})
            
            # 텍스트 검색 조건 - 통합 검색 로직 (Enhanced Learning + Document Chunk)
            if query:
                search_conditions = [
                    # 텍스트 내용 검색
                    {"content": {"$regex": query, "$options": "i"}},
                    {"response": {"$regex": query, "$options": "i"}},
                    {"message": {"$regex": query, "$options": "i"}},
                    
                    # 키워드 및 태그 검색 (배열 필드 개선)
                    {"keywords": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                    {"tags": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                    {"keywords": {"$in": [query]}},  # 정확 일치도 포함
                    {"tags": {"$in": [query]}},
                    
                    # 카테고리 및 주제 검색
                    {"category": {"$regex": query, "$options": "i"}},
                    {"topic": {"$regex": query, "$options": "i"}},
                    
                    # 파일명 검색 (Enhanced Learning + Document Chunk 호환)
                    {"filename": {"$regex": query, "$options": "i"}},
                    {"source_file": {"$regex": query, "$options": "i"}},
                    {"metadata.filename": {"$regex": query, "$options": "i"}},  # Document Chunk용
                    
                    # 소스 및 메타데이터 검색
                    {"source": {"$regex": query, "$options": "i"}},
                    {"upload_type": {"$regex": query, "$options": "i"}},
                    {"metadata.source": {"$regex": query, "$options": "i"}},  # Document Chunk용
                    {"metadata.upload_type": {"$regex": query, "$options": "i"}},  # Document Chunk용
                    
                    # Document Chunk 전용 메타데이터 검색
                    {"metadata.file_extension": {"$regex": query, "$options": "i"}},
                    {"metadata.uploader_email": {"$regex": query, "$options": "i"}}
                ]
                base_filters.append({"$or": search_conditions})
            
            # 최종 검색 쿼리 조합
            if base_filters:
                search_query = {"$and": base_filters} if len(base_filters) > 1 else base_filters[0]
            else:
                search_query = {}
            
            # MongoDB에서 통합 검색 실행
            logger.info(f"🔍 검색 쿼리: {search_query}")
            
            # 통합 검색: Enhanced Learning + Document Chunk 모두 검색
            all_results = []
            
            # 1단계: Enhanced Learning 데이터 검색
            enhanced_query = search_query.copy() if search_query else {}
            enhanced_query["memory_type"] = "enhanced_learning"
            
            enhanced_cursor = self.memories.find(enhanced_query).sort([
                ("shared_to_all", -1),  # 공유 데이터 우선
                ("timestamp", -1)       # 최신순
            ]).limit(limit)
            enhanced_results = list(enhanced_cursor)
            all_results.extend(enhanced_results)
            logger.info(f"🎯 Enhanced Learning 검색 결과: {len(enhanced_results)}개")
            
            # 2단계: Document Chunk 데이터 검색 (기존 API로 저장된 데이터)
            remaining_limit = max(0, limit - len(enhanced_results))
            if remaining_limit > 0:
                # 기존 ID 제외
                existing_ids = [r["_id"] for r in enhanced_results]
                
                document_query = search_query.copy() if search_query else {}
                document_query["memory_type"] = "document_chunk"
                if existing_ids:
                    document_query["_id"] = {"$nin": existing_ids}
                
                document_cursor = self.memories.find(document_query).sort([
                    ("metadata.shared_to_all", -1),  # 메타데이터의 공유 플래그
                    ("timestamp", -1)
                ]).limit(remaining_limit)
                document_results = list(document_cursor)
                all_results.extend(document_results)
                logger.info(f"📄 Document Chunk 검색 결과: {len(document_results)}개")
            
            # 3단계: 여전히 부족하면 다른 타입도 검색
            remaining_limit = max(0, limit - len(all_results))
            if remaining_limit > 0:
                existing_ids = [r["_id"] for r in all_results]
                
                other_query = search_query.copy() if search_query else {}
                other_query["memory_type"] = {"$nin": ["enhanced_learning", "document_chunk"]}
                if existing_ids:
                    other_query["_id"] = {"$nin": existing_ids}
                
                other_cursor = self.memories.find(other_query).sort([
                    ("timestamp", -1)
                ]).limit(remaining_limit)
                other_results = list(other_cursor)
                all_results.extend(other_results)
                logger.info(f"📚 기타 타입 검색 결과: {len(other_results)}개")
            
            results = all_results
            logger.info(f"📚 총 검색 결과: {len(results)}개")
            
            # 관련성 점수 계산 및 정렬
            if query and results:
                query_lower = query.lower()
                for result in results:
                    score = 0
                    content = result.get("content", result.get("response", "")).lower()
                    keywords = result.get("keywords", result.get("tags", []))
                    topic = result.get("topic", result.get("category", "")).lower()
                    filename = result.get("filename", result.get("source_file", "")).lower()
                    
                    # 정확한 매치에 높은 점수
                    if query_lower in content:
                        score += 3
                    if query_lower in topic:
                        score += 2
                    if query_lower in filename:
                        score += 2
                    if any(query_lower in str(kw).lower() for kw in keywords):
                        score += 2
                    
                    # 부분 매치에 낮은 점수
                    query_words = query_lower.split()
                    for word in query_words:
                        if word in content:
                            score += 1
                        if word in topic:
                            score += 0.5
                    
                    result["relevance_score"] = score
                
                # 관련성 점수로 정렬
                results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                results = results[:limit]
            
            # ObjectId를 문자열로 변환
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])
                if "timestamp" in result and hasattr(result["timestamp"], "isoformat"):
                    result["timestamp"] = result["timestamp"].isoformat()
            
            logger.info(f"✅ 학습 내용 회상 완료 - 쿼리: '{query}', 결과: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"❌ 학습 내용 회상 오류: {str(e)}")
            return []
    
    async def get_learned_files_list(self) -> List[Dict]:
        """학습된 파일 목록 조회"""
        if not self.is_connected():
            logger.warning("MongoDB 연결이 없어 학습된 파일 목록 조회를 건너뜁니다")
            return []
            
        try:
            # 파일별 청크 개수 집계
            pipeline = [
                {"$match": {"memory_type": "document_chunk"}},
                {"$group": {
                    "_id": "$filename",
                    "chunk_count": {"$sum": 1},
                    "latest_timestamp": {"$max": "$timestamp"},
                    "file_extension": {"$first": "$file_extension"}
                }},
                {"$sort": {"latest_timestamp": -1}}
            ]
            
            results = list(self.memories.aggregate(pipeline))
            
            # 결과 포맷팅
            file_list = []
            for result in results:
                file_info = {
                    "filename": result["_id"],
                    "chunk_count": result["chunk_count"],
                    "file_extension": result.get("file_extension", ""),
                    "latest_timestamp": result["latest_timestamp"].isoformat() if hasattr(result["latest_timestamp"], "isoformat") else str(result["latest_timestamp"])
                }
                file_list.append(file_info)
            
            logger.info(f"✅ 학습된 파일 목록 조회 완료 - {len(file_list)}개 파일")
            return file_list
            
        except Exception as e:
            logger.error(f"❌ 학습된 파일 목록 조회 오류: {str(e)}")
            return []
    
    async def get_learning_statistics(self) -> Dict:
        """학습 통계 조회"""
        if not self.is_connected():
            logger.warning("MongoDB 연결이 없어 학습 통계 조회를 건너뜁니다")
            return {
                "total_memories": 0,
                "document_chunks": 0,
                "conversations": 0,
                "file_count": 0,
                "connection_status": "disconnected"
            }
            
        try:
            # 전체 메모리 수
            total_memories = self.memories.count_documents({})
            
            # 문서 청크 수
            document_chunks = self.memories.count_documents({"memory_type": "document_chunk"})
            
            # 대화 기록 수
            conversations = self.memories.count_documents({"memory_type": "conversation"})
            
            # 파일별 통계
            file_stats = await self.get_learned_files_list()
            
            # 최근 학습 활동
            recent_learning = list(self.memories.find({}).sort("timestamp", -1).limit(10))
            for item in recent_learning:
                if "_id" in item:
                    item["_id"] = str(item["_id"])
                if "timestamp" in item and hasattr(item["timestamp"], "isoformat"):
                    item["timestamp"] = item["timestamp"].isoformat()
            
            statistics = {
                "total_memories": total_memories,
                "document_chunks": document_chunks,
                "conversations": conversations,
                "learned_files_count": len(file_stats),
                "learned_files": file_stats,
                "recent_learning": recent_learning
            }
            
            logger.info(f"✅ 학습 통계 조회 완료")
            return statistics
            
        except Exception as e:
            logger.error(f"❌ 학습 통계 조회 오류: {str(e)}")
            return {
                "total_memories": 0,
                "document_chunks": 0,
                "conversations": 0,
                "learned_files_count": 0,
                "learned_files": [],
                "recent_learning": []
            }
    
    async def _save_emotion_memory(self, memory_id: str, emotion_data: Dict, timestamp: datetime):
        """감정 메모리 저장"""
        emotion_memory = {
            "memory_id": memory_id,
            "timestamp": timestamp,
            "emotion_label": emotion_data.get("label", "neutral"),
            "emotion_score": emotion_data.get("score", 0.0),
            "emotion_intensity": emotion_data.get("intensity", 0.0),
            "emotion_context": emotion_data.get("context", ""),
            "valence": emotion_data.get("valence", 0.0),
            "arousal": emotion_data.get("arousal", 0.0)
        }
        self.emotion_memories.insert_one(emotion_memory)
    
    async def _save_belief_memory(self, memory_id: str, belief_data: Dict, timestamp: datetime):
        """신념 메모리 저장"""
        belief_memory = {
            "memory_id": memory_id,
            "timestamp": timestamp,
            "belief_tags": belief_data.get("tags", []),
            "belief_strength": belief_data.get("strength", 0.0),
            "belief_context": belief_data.get("context", ""),
            "belief_type": belief_data.get("type", "general")
        }
        self.belief_memories.insert_one(belief_memory)
    
    async def _save_context_memory(self, memory_id: str, context_data: Dict, timestamp: datetime):
        """맥락 메모리 저장"""
        context_memory = {
            "memory_id": memory_id,
            "timestamp": timestamp,
            "context_keywords": context_data.get("keywords", []),
            "context_type": context_data.get("type", "general"),
            "context_importance": context_data.get("importance", 0.0),
            "context_relations": context_data.get("relations", [])
        }
        self.context_memories.insert_one(context_memory)
    
    async def recall_memories(self, 
                            user_id: str,
                            query: str,
                            recall_type: str = "comprehensive",
                            limit: int = None) -> List[Dict]:
        """다중 전략 메모리 회상"""
        try:
            limit = limit or self.recall_limit
            recalled_memories = []
            
            if recall_type == "comprehensive":
                # 종합 회상: 모든 전략 사용
                recalled_memories = await self._comprehensive_recall(user_id, query, limit)
            elif recall_type == "emotion":
                # 감정 기반 회상
                recalled_memories = await self._emotion_based_recall(user_id, query, limit)
            elif recall_type == "context":
                # 맥락 기반 회상
                recalled_memories = await self._context_based_recall(user_id, query, limit)
            elif recall_type == "belief":
                # 신념 기반 회상
                recalled_memories = await self._belief_based_recall(user_id, query, limit)
            elif recall_type == "semantic":
                # 의미 기반 회상
                recalled_memories = await self._semantic_recall(user_id, query, limit)
            else:
                # 기본 키워드 기반 회상
                recalled_memories = await self._keyword_recall(user_id, query, limit)
            
            # 회상 결과 정제 및 정렬
            cleaned_memories = self._clean_recall_results(recalled_memories)
            sorted_memories = self._sort_recall_results(cleaned_memories, query)
            
            # 접근 기록 업데이트
            await self._update_access_records([m["_id"] for m in sorted_memories])
            
            logger.info(f"메모리 회상 완료 - 사용자: {user_id}, 쿼리: {query}, 결과: {len(sorted_memories)}개")
            return sorted_memories
            
        except Exception as e:
            logger.error(f"메모리 회상 오류: {str(e)}")
            return []
    
    async def enhanced_recall(self, query: str, user_id: str, limit: int = 5) -> List[Dict]:
        """
        향상된 회상 시스템 - 학습된 내용(전체 공유) + 개인 대화 기록 결합
        
        Args:
            query (str): 검색 쿼리
            user_id (str): 사용자 ID (개인 대화 기록용)
            limit (int): 최대 결과 수
            
        Returns:
            List[Dict]: 회상된 메모리 목록
        """
        if not self.is_connected():
            logger.warning("MongoDB 연결이 없어 메모리 회상을 건너뜁니다")
            return []
            
        try:
            all_memories = []
            
            # 1. 학습된 내용 회상 (모든 사용자 공유)
            # document_chunk 타입은 관리자가 학습한 내용으로 모든 사용자가 공유
            learned_memories = await self.recall_learned_content(
                query=query,
                memory_type="document_chunk",
                limit=max(3, limit // 2)  # 전체 한도의 절반 이상을 학습 내용에 할당
            )
            
            if learned_memories:
                # 학습된 내용에 표시 추가
                for memory in learned_memories:
                    memory["recall_type"] = "learned_content"
                    memory["is_shared"] = True
                all_memories.extend(learned_memories)
                logger.info(f"📚 학습된 내용 회상: {len(learned_memories)}개")
            
            # 2. 개인 대화 기록 회상 (사용자별)
            personal_limit = limit - len(learned_memories)
            if personal_limit > 0:
                personal_memories = await self.recall_memories(
                    user_id=user_id,
                    query=query,
                    recall_type="comprehensive",
                    limit=personal_limit
                )
                
                if personal_memories:
                    # 개인 대화 내용에 표시 추가
                    for memory in personal_memories:
                        memory["recall_type"] = "personal_conversation"
                        memory["is_shared"] = False
                    all_memories.extend(personal_memories)
                    logger.info(f"👤 개인 대화 회상: {len(personal_memories)}개")
            
            # 3. 결과 정렬 및 중복 제거
            # 관련성 점수와 중요도를 기준으로 정렬
            unique_memories = {}
            for memory in all_memories:
                memory_id = str(memory.get("_id", ""))
                if memory_id not in unique_memories:
                    unique_memories[memory_id] = memory
            
            final_memories = list(unique_memories.values())
            
            # 학습된 내용을 우선순위로 정렬
            final_memories.sort(key=lambda x: (
                x.get("is_shared", False),  # 학습된 내용 우선
                x.get("importance_score", 0),  # 중요도 점수
                x.get("relevance_score", 0)  # 관련성 점수
            ), reverse=True)
            
            # 한도 적용
            final_memories = final_memories[:limit]
            
            logger.info(f"✅ 통합 회상 완료 - 총 {len(final_memories)}개 (학습: {len(learned_memories)}, 개인: {len(all_memories) - len(learned_memories)})")
            return final_memories
            
        except Exception as e:
            logger.error(f"❌ 향상된 회상 오류: {str(e)}")
            return []
    
    async def _comprehensive_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """종합 회상 전략"""
        all_memories = []
        
        # 1. 감정 기반 회상
        emotion_memories = await self._emotion_based_recall(user_id, query, limit // 3)
        all_memories.extend(emotion_memories)
        
        # 2. 맥락 기반 회상
        context_memories = await self._context_based_recall(user_id, query, limit // 3)
        all_memories.extend(context_memories)
        
        # 3. 의미 기반 회상
        semantic_memories = await self._semantic_recall(user_id, query, limit // 3)
        all_memories.extend(semantic_memories)
        
        # 중복 제거 및 정렬
        unique_memories = self._remove_duplicates(all_memories)
        return unique_memories[:limit]
    
    async def _emotion_based_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """감정 기반 회상"""
        # 쿼리에서 감정 키워드 추출
        emotion_keywords = self._extract_emotion_keywords(query)
        
        if not emotion_keywords:
            return []
        
        # 감정 메모리에서 검색
        emotion_query = {
            "emotion_label": {"$in": emotion_keywords},
            "user_id": user_id
        }
        
        memories = list(self.memories.find(emotion_query)
                       .sort([("emotion_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _context_based_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """맥락 기반 회상"""
        # 쿼리에서 맥락 키워드 추출
        context_keywords = self._extract_context_keywords(query)
        
        if not context_keywords:
            return []
        
        # 맥락 메모리에서 검색
        context_query = {
            "context_keywords": {"$in": context_keywords},
            "user_id": user_id
        }
        
        memories = list(self.memories.find(context_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _belief_based_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """신념 기반 회상"""
        # 쿼리에서 신념 키워드 추출
        belief_keywords = self._extract_belief_keywords(query)
        
        if not belief_keywords:
            return []
        
        # 신념 메모리에서 검색
        belief_query = {
            "belief_tags": {"$in": belief_keywords},
            "user_id": user_id
        }
        
        memories = list(self.memories.find(belief_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _semantic_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """의미 기반 회상"""
        # 쿼리 키워드 추출
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            return []
        
        # 의미적 유사성 검색
        semantic_query = {
            "user_id": user_id,
            "$or": [
                {"user_input": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"ai_response": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"summary": {"$regex": "|".join(query_keywords), "$options": "i"}}
            ]
        }
        
        memories = list(self.memories.find(semantic_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _keyword_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """키워드 기반 회상"""
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            return []
        
        # 키워드 검색
        keyword_query = {
            "user_id": user_id,
            "$or": [
                {"user_input": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"ai_response": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"topic": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"sub_topic": {"$regex": "|".join(query_keywords), "$options": "i"}}
            ]
        }
        
        memories = list(self.memories.find(keyword_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    def _extract_emotion_keywords(self, text: str) -> List[str]:
        """감정 키워드 추출"""
        emotion_keywords = [
            "기쁨", "행복", "즐거움", "만족", "감사", "사랑", "희망", "열정",
            "슬픔", "우울", "절망", "외로움", "그리움", "아픔", "상실",
            "분노", "화남", "짜증", "불만", "적대감", "원망",
            "불안", "걱정", "두려움", "긴장", "스트레스", "압박감",
            "놀람", "충격", "당황", "혼란", "의아함",
            "평온", "차분", "여유", "안정", "편안"
        ]
        
        found_emotions = []
        for emotion in emotion_keywords:
            if emotion in text:
                found_emotions.append(emotion)
        
        return found_emotions
    
    def _extract_context_keywords(self, text: str) -> List[str]:
        """맥락 키워드 추출"""
        context_patterns = [
            r"집에서", r"회사에서", r"학교에서", r"카페에서", r"길에서",
            r"아침에", r"점심에", r"저녁에", r"밤에", r"새벽에",
            r"친구와", r"가족과", r"동료와", r"선생님과", r"의사와",
            r"코딩", r"프로그래밍", r"개발", r"학습", r"공부",
            r"음악", r"영화", r"책", r"운동", r"요리"
        ]
        
        context_keywords = []
        for pattern in context_patterns:
            matches = re.findall(pattern, text)
            context_keywords.extend(matches)
        
        return list(set(context_keywords))
    
    def _extract_belief_keywords(self, text: str) -> List[str]:
        """신념 키워드 추출"""
        belief_keywords = [
            "믿음", "신념", "가치관", "철학", "원칙", "도덕", "윤리",
            "정의", "평등", "자유", "책임", "성실", "정직", "용기",
            "인내", "겸손", "배려", "존중", "사랑", "희생", "봉사"
        ]
        
        found_beliefs = []
        for belief in belief_keywords:
            if belief in text:
                found_beliefs.append(belief)
        
        return found_beliefs
    
    def _extract_keywords(self, text: str) -> List[str]:
        """일반 키워드 추출"""
        # 불용어 제거
        stop_words = ["이", "가", "을", "를", "의", "에", "에서", "로", "으로", "와", "과", "도", "만", "은", "는", "이", "그", "저", "우리", "너", "나"]
        
        # 단어 분리 및 필터링
        words = re.findall(r'\w+', text)
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:10]  # 상위 10개 키워드만 반환
    
    def _extract_topic(self, text: str) -> str:
        """주제 추출"""
        topics = {
            "감정": ["기분", "느낌", "감정", "마음", "심정"],
            "일상": ["일", "생활", "루틴", "하루", "일상"],
            "관계": ["친구", "가족", "사람", "관계", "대화"],
            "학습": ["공부", "학습", "배우", "지식", "교육"],
            "기술": ["코딩", "프로그래밍", "개발", "기술", "코드"],
            "철학": ["의미", "존재", "생명", "우주", "진리", "철학"],
            "건강": ["건강", "운동", "병", "의사", "약"],
            "취미": ["취미", "관심", "좋아", "즐겨", "재미"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text for keyword in keywords):
                return topic
        
        return "일반"
    
    def _extract_sub_topic(self, text: str) -> str:
        """하위 주제 추출"""
        # 더 구체적인 하위 주제 추출 로직
        return "일반"
    
    def _generate_summary(self, user_input: str, ai_response: str) -> str:
        """메모리 요약 생성"""
        # 간단한 요약 생성 (실제로는 더 정교한 요약 알고리즘 사용)
        combined = f"{user_input} → {ai_response}"
        if len(combined) > 200:
            return combined[:200] + "..."
        return combined
    
    def _calculate_importance(self, user_input: str, ai_response: str, consciousness_level: float) -> float:
        """중요도 점수 계산"""
        importance = 0.5  # 기본 점수
        
        # 의식 수준에 따른 가중치
        importance += consciousness_level * 0.3
        
        # 감정 키워드가 있으면 가중치 증가
        if self._extract_emotion_keywords(user_input):
            importance += 0.2
        
        # 철학적 키워드가 있으면 가중치 증가
        if any(word in user_input for word in ["의미", "존재", "생명", "우주", "진리"]):
            importance += 0.3
        
        # 응답 길이에 따른 가중치
        if len(ai_response) > 100:
            importance += 0.1
        
        return min(1.0, importance)
    
    async def _update_connections(self, memory_id: str, user_input: str, ai_response: str):
        """연결 관계 업데이트"""
        # 유사한 메모리들과의 연결 생성
        similar_memories = await self._find_similar_memories(user_input, ai_response)
        
        if similar_memories:
            # 현재 메모리에 연결 정보 추가
            self.memories.update_one(
                {"_id": ObjectId(memory_id)},
                {"$set": {"connections": [str(m["_id"]) for m in similar_memories]}}
            )
    
    async def _find_similar_memories(self, user_input: str, ai_response: str) -> List[Dict]:
        """유사한 메모리 찾기"""
        # 간단한 유사도 검색 (실제로는 더 정교한 알고리즘 사용)
        keywords = self._extract_keywords(user_input)
        
        if not keywords:
            return []
        
        # 키워드 기반 유사 메모리 검색
        similar_query = {
            "$or": [
                {"user_input": {"$regex": "|".join(keywords[:3]), "$options": "i"}},
                {"ai_response": {"$regex": "|".join(keywords[:3]), "$options": "i"}}
            ]
        }
        
        similar_memories = list(self.memories.find(similar_query)
                              .sort("timestamp", -1)
                              .limit(5))
        
        return similar_memories
    
    def _clean_recall_results(self, memories: List[Dict]) -> List[Dict]:
        """회상 결과 정제"""
        cleaned = []
        
        for memory in memories:
            # 필수 필드 확인
            if not all(key in memory for key in ["user_input", "ai_response", "timestamp"]):
                continue
            
            # 빈 내용 제거
            if not memory["user_input"].strip() or not memory["ai_response"].strip():
                continue
            
            # 너무 오래된 메모리 제거 (1년 이상)
            memory_date = memory["timestamp"]
            if isinstance(memory_date, str):
                memory_date = datetime.fromisoformat(memory_date.replace('Z', '+00:00'))
            
            if memory_date < datetime.now() - timedelta(days=365):
                continue
            
            cleaned.append(memory)
        
        return cleaned
    
    def _sort_recall_results(self, memories: List[Dict], query: str) -> List[Dict]:
        """회상 결과 정렬"""
        def sort_key(memory):
            score = 0.0
            
            # 중요도 점수
            score += memory.get("importance_score", 0.0) * 0.4
            
            # 최근성 점수
            memory_date = memory["timestamp"]
            if isinstance(memory_date, str):
                memory_date = datetime.fromisoformat(memory_date.replace('Z', '+00:00'))
            
            days_old = (datetime.now() - memory_date).days
            recency_score = max(0, 1 - (days_old / 365))
            score += recency_score * 0.3
            
            # 접근 빈도 점수
            access_count = memory.get("access_count", 0)
            score += min(1.0, access_count / 10) * 0.2
            
            # 쿼리 관련성 점수
            query_keywords = self._extract_keywords(query)
            memory_text = f"{memory['user_input']} {memory['ai_response']}"
            relevance_score = sum(1 for keyword in query_keywords if keyword in memory_text) / len(query_keywords) if query_keywords else 0
            score += relevance_score * 0.1
            
            return score
        
        return sorted(memories, key=sort_key, reverse=True)
    
    async def _update_access_records(self, memory_ids: List[str]):
        """접근 기록 업데이트"""
        for memory_id in memory_ids:
            self.memories.update_one(
                {"_id": ObjectId(memory_id)},
                {
                    "$set": {"last_accessed": datetime.now()},
                    "$inc": {"access_count": 1}
                }
            )
    
    def _remove_duplicates(self, memories: List[Dict]) -> List[Dict]:
        """중복 메모리 제거"""
        seen_ids = set()
        unique_memories = []
        
        for memory in memories:
            memory_id = str(memory["_id"])
            if memory_id not in seen_ids:
                seen_ids.add(memory_id)
                unique_memories.append(memory)
        
        return unique_memories
    
    async def get_memory_stats(self, user_id: str) -> Dict:
        """메모리 통계 조회"""
        try:
            total_memories = self.memories.count_documents({"user_id": user_id})
            
            # 감정별 통계
            emotion_stats = list(self.memories.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$emotion_label", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            # 주제별 통계
            topic_stats = list(self.memories.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$topic", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            # 최근 메모리
            recent_memories = list(self.memories.find({"user_id": user_id})
                                 .sort("timestamp", -1)
                                 .limit(5))
            
            return {
                "total_memories": total_memories,
                "emotion_stats": emotion_stats,
                "topic_stats": topic_stats,
                "recent_memories": recent_memories
            }
            
        except Exception as e:
            logger.error(f"메모리 통계 조회 오류: {str(e)}")
            return {"error": str(e)}
    
    # ===================== 회상 기능 메서드들 =====================
    
    async def enhanced_recall(self, query: str, user_id: str = None, limit: int = 5):
        """향상된 회상 기능 - RecallEngine 또는 경량 memory_manager 활용"""
        if not self.memory_manager or not self.memory_manager.is_initialized:
            logger.warning("memory_manager가 초기화되지 않아 기본 회상 사용")
            return await self._basic_recall(query, user_id, limit)
        
        try:
            # 경량 memory_manager인지 확인
            manager_type = type(self.memory_manager).__name__
            
            if manager_type == "LightweightMemoryManager":
                # 경량 버전은 직접 호출
                logger.info("🚂 Railway 경량 memory_manager로 회상")
                results = await self.memory_manager.recall_memories_async(query, limit)
                logger.info(f"✅ 경량 memory_manager 회상 완료: {len(results)}개 결과")
                return results
            else:
                # 전체 기능 RecallEngine 사용
                from aura_system.recall_engine import RecallEngine
                
                recall_engine = RecallEngine(self.memory_manager)
                context = {"user_id": user_id} if user_id else {}
                
                results = await recall_engine.recall(
                    query=query,
                    context=context,
                    limit=limit
                )
                
                logger.info(f"✅ RecallEngine 회상 완료: {len(results)}개 결과")
                return results
            
        except Exception as e:
            logger.error(f"회상 시스템 실패: {e}")
            return await self._basic_recall(query, user_id, limit)
    
    async def _basic_recall(self, query: str, user_id: str = None, limit: int = 5):
        """기본 회상 기능 (fallback)"""
        try:
            if not self.is_connected():
                return []
            
            # 간단한 텍스트 검색
            search_filter = {}
            if user_id:
                search_filter["user_id"] = user_id
            
            # 키워드 기반 검색
            keywords = query.lower().split()
            search_conditions = []
            
            for keyword in keywords:
                search_conditions.append({"content": {"$regex": keyword, "$options": "i"}})
            
            if search_conditions:
                search_filter["$or"] = search_conditions
            
            # 결과 조회
            results = list(self.memories.find(search_filter)
                          .sort("timestamp", -1)
                          .limit(limit))
            
            logger.info(f"✅ 기본 회상 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"기본 회상 실패: {e}")
            return []
    
    async def recall_learned_content(self, query: str, user_id: str = None, limit: int = 5):
        """학습된 콘텐츠 회상 (문서 기반)"""
        try:
            if not self.is_connected():
                return []
            
            # 문서 타입 필터
            search_filter = {"memory_type": "document_chunk"}
            if user_id:
                search_filter["user_id"] = user_id
            
            # 키워드 검색
            keywords = query.lower().split()
            search_conditions = []
            
            for keyword in keywords:
                search_conditions.append({"content": {"$regex": keyword, "$options": "i"}})
                search_conditions.append({"metadata.filename": {"$regex": keyword, "$options": "i"}})
            
            if search_conditions:
                search_filter["$or"] = search_conditions
            
            # 결과 조회
            results = list(self.memories.find(search_filter)
                          .sort("timestamp", -1)
                          .limit(limit))
            
            logger.info(f"✅ 학습된 콘텐츠 회상 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"학습된 콘텐츠 회상 실패: {e}")
            return []
    
    def get_memory_manager_status(self):
        """memory_manager 상태 확인"""
        if not self.memory_manager:
            return {"status": "not_initialized", "available": False}
        
        return {
            "status": "initialized" if self.memory_manager.is_initialized else "not_initialized",
            "available": self.memory_manager.is_initialized,
            "class": str(type(self.memory_manager).__name__)
        }
    
    async def cleanup_old_memories(self, user_id: str, days: int = 365):
        """오래된 메모리 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 오래된 메모리 삭제
            result = self.memories.delete_many({
                "user_id": user_id,
                "timestamp": {"$lt": cutoff_date},
                "importance_score": {"$lt": 0.5}  # 중요도가 낮은 메모리만
            })
            
            logger.info(f"오래된 메모리 정리 완료 - 사용자: {user_id}, 삭제된 메모리: {result.deleted_count}개")
            return {"deleted_count": result.deleted_count}
            
        except Exception as e:
            logger.error(f"메모리 정리 오류: {str(e)}")
            return {"error": str(e)}

# 전역 메모리 시스템 인스턴스 (지연 초기화)
memory_system = None

def get_eora_memory_system():
    """EORA 메모리 시스템 인스턴스를 반환 (지연 초기화)"""
    global memory_system
    if memory_system is None:
        memory_system = EORAMemorySystem()
    return memory_system 