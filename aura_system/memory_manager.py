"""
memory_manager.py
- 메모리 관리 시스템
- MongoDB와 Redis를 사용한 메모리 저장 및 회상
"""

from datetime import datetime, timedelta
import hashlib
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from bson.objectid import ObjectId, InvalidId
from tiktoken import encoding_for_model
import numpy as np
import logging
import threading
import re
import os
import uuid
import psutil
import subprocess
import signal
import time
import redis
import redis.asyncio as aioredis
from pymongo import MongoClient
import faiss
import pickle
from asyncio import CancelledError

from aura_system.vector_store import FaissIndex, embed_text, embed_text_async
from aura_system.memory_structurer import MemoryAtom
from aura_system.resonance_engine import calculate_resonance
from aura_system.recall_formatter import format_recall
from aura_system.task_manager import get_event_loop, add_task, cleanup_pending_tasks
from aura_system.resource_manager import ResourceManager
from aura_system.config import get_config
from utils.serialization import safe_serialize, safe_mongo_doc, safe_redis_value
from aura_system.insight_engine import analyze_cognitive_layer
from aura_system.memory_chain import find_or_create_chain_id
from aura_system.recall_engine import find_linked_memories
from aura_system.belief_system import update_belief_system
from aura_system.wisdom_extractor import extract_wisdom
from aura_system.meta_cognition import self_check, self_feedback_loop
from aura_system.ethic_filter import ethic_filter

# 사용자 정의 JSON 인코더 추가
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

# 전역 변수
_memory_manager = None
_memory_manager_lock = threading.Lock()
_memory_manager_async_lock = asyncio.Lock()

# 토큰 계산을 위한 인코더 초기화
enc = encoding_for_model("gpt-4o")

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING  # INFO 이하 로그는 출력하지 않음
)
logger = logging.getLogger(__name__)

def count_tokens(text: str) -> int:
    """텍스트의 토큰 수를 계산
    
    Args:
        text (str): 토큰 수를 계산할 텍스트
        
    Returns:
        int: 토큰 수
        
    Raises:
        ValueError: text가 유효하지 않은 경우
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("유효하지 않은 텍스트")

    try:
        return len(enc.encode(text))
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        logger.warning(f"토큰 인코딩 실패, 대체 계산 사용: {e}")
        # 더 정확한 대체 계산
        words = text.split()
        return sum(len(word) // 4 + 1 for word in words)  # 평균 단어 길이 4자 기준
    except Exception as e:
        logger.error(f"토큰 계산 중 예상치 못한 오류: {e}")
        raise

def estimate_emotion(text: str) -> Tuple[str, float]:
    """텍스트의 감정을 분석
    
    Args:
        text (str): 분석할 텍스트
        
    Returns:
        tuple[str, float]: (감정 레이블, 신뢰도)
        
    Raises:
        ValueError: text가 유효하지 않은 경우
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("유효하지 않은 텍스트")

    emotion_map = {
        "기쁨": ["행복", "기쁘다", "만족", "기대", "감사", "즐거움", "감격", "감동", "희망", "웃음", "사랑",
                "happy", "joy", "delight", "pleasure", "gratitude", "excitement"],
        "슬픔": ["슬퍼", "외로움", "상실감", "우울", "눈물", "그리움", "절망", "비애", "허탈", "쓸쓸",
                "sad", "lonely", "depressed", "tears", "hopeless", "grief"],
        "분노": ["화남", "짜증", "분개", "격분", "억울", "질투", "분노", "열받음", "폭발", "불공평",
                "angry", "furious", "rage", "irritated", "jealous", "outraged"],
        "불안": ["불안", "두려움", "긴장", "불확실", "위험", "공포", "망설임", "주저함", "불편", "불신",
                "anxious", "fear", "nervous", "uncertain", "danger", "afraid"],
        "놀람": ["놀람", "경악", "충격", "예상밖", "뜻밖", "경이", "깜짝", "멍해짐", "망연자실",
                "surprised", "shocked", "amazed", "astonished", "stunned"],
        "혐오": ["싫다", "혐오", "불쾌", "거부", "역겹다", "불결", "비위상함", "혐오감", "질림",
                "disgust", "hate", "repulsive", "reject", "dislike"],
        "자신감": ["자신감", "결단력", "의욕", "용기", "의지", "뿌듯", "확신", "단호", "의욕적",
                  "confident", "determined", "courageous", "proud", "certain"],
        "부끄러움": ["창피", "당황", "수줍", "민망", "부끄러움", "머쓱", "쑥스러움", "겸연쩍",
                    "shy", "embarrassed", "ashamed", "awkward", "uncomfortable"],
        "혼란": ["혼란", "혼동", "모르겠다", "갈피", "뒤죽박죽", "혼란스러움",
                "confused", "puzzled", "uncertain", "chaotic", "disoriented"],
        "기타": ["무감정", "중립", "아무 감정 없음",
                "neutral", "indifferent", "no emotion"]
    }

    text = text.lower()
    max_matches = 0
    best_emotion = "중립"
    best_confidence = 0.5

    for label, keywords in emotion_map.items():
        matches = sum(1 for k in keywords if k in text)
        if matches > max_matches:
            max_matches = matches
            best_emotion = label
            best_confidence = min(0.5 + (matches * 0.1), 0.9)

    return best_emotion, best_confidence

def _format_memories_for_logging(memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """로깅을 위해 메모리 목록의 일부 필드를 축약합니다."""
    if not isinstance(memories, list):
        return []
        
    formatted_memories = []
    for mem in memories:
        if not isinstance(mem, dict):
            continue
        
        # 원본 딕셔너리를 복사하여 수정
        log_mem = mem.copy()
        
        # 'embedding' 필드가 있고, 리스트 또는 numpy 배열인 경우 축약
        if 'embedding' in log_mem and isinstance(log_mem['embedding'], (list, np.ndarray)):
            embedding = log_mem['embedding']
            log_mem['embedding'] = f"vector(size={len(embedding)})"

        # 'belief_vector' 필드가 있고 리스트인 경우 축약
        if 'belief_vector' in log_mem and isinstance(log_mem['belief_vector'], list):
            belief_vector = log_mem['belief_vector']
            log_mem['belief_vector'] = f"vector(size={len(belief_vector)})"
            
        formatted_memories.append(log_mem)
        
    return formatted_memories

MAX_HISTORY_TOKENS = 4000

def truncate_history_by_tokens(history: List[Dict[str, Any]], max_tokens: int = MAX_HISTORY_TOKENS) -> List[Dict[str, Any]]:
    """히스토리를 토큰 수에 따라 자름
    
    Args:
        history (List[Dict[str, Any]]): 자를 히스토리
        max_tokens (int): 최대 토큰 수
        
    Returns:
        List[Dict[str, Any]]: 잘린 히스토리
        
    Raises:
        ValueError: history가 리스트가 아니거나 max_tokens가 유효하지 않은 경우
    """
    if not isinstance(history, list):
        raise ValueError("history는 리스트여야 합니다")
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("max_tokens는 양의 정수여야 합니다")

    total = 0
    truncated = []
    for item in reversed(history):
        if not isinstance(item, dict):
            continue
        u, a = item.get("user_input", ""), item.get("gpt_response", "")
        combined = u + "\n" + a
        t = count_tokens(combined)
        if total + t > max_tokens:
            break
        total += t
        truncated.insert(0, item)
    return truncated

def select_top_recall_summaries(recall_data: List[Dict[str, Any]], top_k: int = 5, score_key: str = "score") -> List[Dict[str, Any]]:
    """상위 회상 요약 선택
    
    Args:
        recall_data (List[Dict[str, Any]]): 회상 데이터
        top_k (int): 선택할 상위 개수
        score_key (str): 점수 키
        
    Returns:
        List[Dict[str, Any]]: 선택된 회상 요약
        
    Raises:
        ValueError: recall_data가 리스트가 아니거나 top_k가 유효하지 않은 경우
    """
    if not isinstance(recall_data, list):
        raise ValueError("recall_data는 리스트여야 합니다")
    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("top_k는 양의 정수여야 합니다")

    if not recall_data:
        return []

    def get_sort_key(item: Dict[str, Any]) -> Any:
        return item.get(score_key) or item.get("timestamp", datetime.min)

    sorted_recall = sorted(recall_data, key=get_sort_key, reverse=True)
    return sorted_recall[:top_k]

async def get_memory_manager() -> "MemoryManagerAsync":
    """메모리 매니저 인스턴스를 가져옴
    
    Returns:
        MemoryManagerAsync: 메모리 매니저 인스턴스
        
    Raises:
        RuntimeError: 메모리 매니저 초기화 실패
    """
    global _memory_manager
    if _memory_manager is None:
        async with _memory_manager_async_lock:
            if _memory_manager is None:
                try:
                    _memory_manager = await MemoryManagerAsync.get_instance()
                except Exception as e:
                    logger.error(f"메모리 매니저 초기화 실패: {str(e)}")
                    _memory_manager = None
                    raise RuntimeError(f"메모리 매니저 초기화 실패: {str(e)}")
    return _memory_manager

def get_memory_manager_sync() -> "MemoryManagerAsync":
    """동기 코드에서 메모리 매니저 인스턴스를 안전하게 가져옵니다."""
    global _memory_manager
    with _memory_manager_lock:
        if _memory_manager is None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 이미 실행 중인 루프가 있으면 nest_asyncio를 사용해 중첩 실행 허용
                    import nest_asyncio
                    nest_asyncio.apply()
                    # 비동기 함수를 현재 루프에서 실행
                    future = asyncio.run_coroutine_threadsafe(get_memory_manager(), loop)
                    _memory_manager = future.result()
                else:
                    # 실행 중인 루프가 없으면 새 루프에서 실행
                    _memory_manager = loop.run_until_complete(get_memory_manager())
                
                # logger.info("✅ 동기 컨텍스트에서 MemoryManager 인스턴스 초기화 완료")
            except Exception as e:
                logger.error(f"동기 MemoryManager 초기화 중 치명적 오류 발생: {e}", exc_info=True)
                _memory_manager = None # 실패 시 인스턴스 리셋
                raise RuntimeError(f"Failed to initialize MemoryManager synchronously: {e}")
    return _memory_manager

class MemoryManagerAsync:
    _instance = None
    _loop = None
    _redis_pool = None
    _redis_server_process = None
    _init_lock = asyncio.Lock()
    _lock = asyncio.Lock()
    _initialization_timeout = 120  # 120초로 증가
    _max_retries = 5  # 최대 재시도 횟수 증가
    _faiss_index_path = "faiss_index.idx"
    _id_map_path = "faiss_id_map.pkl"
    
    @classmethod
    def _find_redis_server(cls) -> str:
        """Redis 서버 실행 파일 경로 찾기"""
        try:
            # 1. 현재 디렉토리 확인
            current_dir = os.path.dirname(__file__)
            redis_path = os.path.join(current_dir, "redis-server.exe")
            if os.path.exists(redis_path):
                return redis_path
            
            # 2. 기본 설치 경로 확인
            default_path = os.path.join("C:\\Program Files\\Redis", "redis-server.exe")
            if os.path.exists(default_path):
                return default_path
            
            # 3. PATH에서 찾기
            redis_cmd = 'redis-server'
            if os.name == 'nt':  # Windows
                redis_cmd = 'redis-server.exe'
            
            return redis_cmd
        except Exception as e:
            logger.error(f"Redis 서버 실행 파일을 찾을 수 없음: {e}")
            raise FileNotFoundError("redis-server.exe를 찾을 수 없습니다. Redis가 설치되어 있는지 확인해주세요.")

    async def _start_redis_server(self):
        """Redis 서버 시작"""
        try:
            # 이미 실행 중인 Redis 서버 확인
            for proc in psutil.process_iter(['pid', 'name']):
                if 'redis-server' in proc.info['name'].lower():
                    # logger.info("Redis 서버가 이미 실행 중입니다.")
                    return True

            # Redis 서버 실행 파일 찾기
            redis_server = self._find_redis_server()
            if not redis_server:
                logger.error("Redis 서버 실행 파일을 찾을 수 없습니다.")
                return False

            # 임시 디렉토리 생성
            temp_dir = os.path.join(os.getcwd(), 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Redis 설정 파일 생성
            redis_conf = os.path.join(temp_dir, 'redis.conf')
            with open(redis_conf, 'w') as f:
                f.write(f"""
bind 127.0.0.1
port 6379
dir {temp_dir}
dbfilename dump.rdb
maxmemory 100mb
maxmemory-policy allkeys-lru
appendonly yes
appendfilename "appendonly.aof"
loglevel notice
logfile "{os.path.join(temp_dir, 'redis.log')}"
""")

            # Redis 서버 시작
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.redis_process = subprocess.Popen(
                    [redis_server, redis_conf],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:  # Linux/Mac
                self.redis_process = subprocess.Popen(
                    [redis_server, redis_conf],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            # 연결 테스트
            for _ in range(5):
                try:
                    redis = await aioredis.from_url(
                        "redis://localhost:6379",
                        encoding="utf-8",
                        decode_responses=True
                    )
                    await redis.ping()
                    await redis.close()
                    # logger.info("Redis 서버가 성공적으로 시작되었습니다.")
                    return True
                except Exception as e:
                    logger.warning(f"Redis 연결 시도 중: {str(e)}")
                    await asyncio.sleep(1)

            logger.error("Redis 서버 연결 실패")
            return False

        except Exception as e:
            logger.error(f"Redis 서버 시작 중 오류 발생: {str(e)}")
            return False

    @classmethod
    def _stop_redis_server(cls):
        """Redis 서버 종료"""
        try:
            if cls._redis_server_process is not None:
                # Windows 환경에서의 특별 처리
                if os.name == 'nt':
                    try:
                        # 프로세스 종료
                        cls._redis_server_process.terminate()
                        cls._redis_server_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # 강제 종료
                        cls._redis_server_process.kill()
                        cls._redis_server_process.wait()
                else:
                    # Linux/Mac 환경
                    cls._redis_server_process.terminate()
                    cls._redis_server_process.wait()

                # 자식 프로세스 정리
                for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                    if proc.info['name'] and 'redis-server' in proc.info['name'].lower():
                        try:
                            proc.terminate()
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            proc.kill()

                cls._redis_server_process = None
                # logger.info("✅ Redis 서버 종료 완료")

        except Exception as e:
            logger.error(f"❌ Redis 서버 종료 중 오류 발생: {e}")
            # 오류가 발생해도 프로세스는 정리
            cls._redis_server_process = None

    @classmethod
    def _create_redis_pool(cls):
        """Redis 연결 풀 생성"""
        try:
            # Windows 서비스로 실행 중인 Redis에 연결
            if os.name == 'nt':
                return redis.ConnectionPool(
                    host='127.0.0.1',
                    port=6379,
                    db=0,
                    decode_responses=True,
                    socket_timeout=3,  # 소켓 타임아웃 단축 (5초 → 3초)
                    socket_connect_timeout=3,  # 연결 타임아웃 단축 (5초 → 3초)
                    retry_on_timeout=True
                )
            else:
                return redis.ConnectionPool(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
        except Exception as e:
            logger.error(f"❌ Redis 연결 풀 생성 실패: {e}")
            raise

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            async with cls._init_lock:
                if cls._instance is None:
                    try:
                        cls._instance = cls()
                        await cls._instance.initialize()
                    except Exception as e:
                        cls._instance = None
                        raise
        return cls._instance

    @classmethod
    def get_instance_sync(cls):
        """동기 환경에서 안전하게 인스턴스를 반환
        
        Returns:
            MemoryManagerAsync: 메모리 매니저 인스턴스
            
        Raises:
            RuntimeError: 메모리 매니저 초기화 실패
        """
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    if loop.is_running():
                        import nest_asyncio
                        nest_asyncio.apply()
                    
                    try:
                        # 비동기 초기화를 동기적으로 실행
                        async def init_instance():
                            instance = await cls.get_instance()
                            await instance.initialize()
                            return instance
                        
                        cls._instance = loop.run_until_complete(init_instance())
                    except Exception as e:
                        cls._instance = None
                        raise RuntimeError(f"MemoryManager 초기화 실패: {str(e)}")
        return cls._instance

    def __init__(self):
        """초기화"""
        # 중복 초기화 방지
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.config = get_config()
        self.resource_manager = ResourceManager()
        self.is_initialized = False
        self.faiss_index = None
        self.faiss_id_map = None
        self._loop = get_event_loop()
        self._initialized = True # 초기화 시작 플래그

    async def _create_mongo_indexes(self):
        """MongoDB memories 컬렉션에 인덱스 생성"""
        try:
            if self.resource_manager and self.resource_manager.memories is not None:
                await asyncio.to_thread(self.resource_manager.memories.create_index, [("timestamp", -1)])
                # 텍스트 인덱스는 이미 존재할 수 있으므로 에러 핸들링이 필요할 수 있습니다.
                # await asyncio.to_thread(self.resource_manager.memories.create_index, [("content", "text")])
            else:
                logger.error("MongoDB memories 컬렉션이 초기화되지 않아 인덱스를 생성할 수 없습니다.")
        except Exception as e:
            logger.error(f"MongoDB 인덱스 생성 실패: {e}", exc_info=True)

    async def _load_faiss_index(self):
        """FAISS 인덱스를 로드합니다."""
        try:
            if os.path.exists(self._faiss_index_path) and os.path.exists(self._id_map_path):
                self.faiss_index = faiss.read_index(self._faiss_index_path)
                with open(self._id_map_path, "rb") as f:
                    self.faiss_id_map = pickle.load(f)
            else:
                logger.warning("FAISS 인덱스 파일이 없어 로드를 건너뜁니다. 필요 시 `build_faiss_index.py`를 실행하세요.")
                self.faiss_index = None
                self.faiss_id_map = []
        except Exception as e:
            logger.error(f"FAISS 인덱스 로드 실패: {e}", exc_info=True)
            self.faiss_index = None
            self.faiss_id_map = []

    async def initialize(self):
        """
        MemoryManagerAsync의 비동기 초기화를 수행합니다.
        MongoDB 및 Redis 연결, 리소스 관리자 초기화, 인덱스 생성 등을 포함합니다.
        """
        if self.is_initialized:
            return

        try:
            # 리소스 관리자 초기화
            await self.resource_manager.initialize()
            
            # MongoDB 인덱스 생성
            await self._create_mongo_indexes()

            # FAISS 인덱스 로드
            await self._load_faiss_index()

            self.is_initialized = True

        except Exception as e:
            self.is_initialized = False
            # 실패 시 리소스 정리
            if self.resource_manager:
                await self.resource_manager.cleanup()
            self._reset_state()
            raise  # 초기화 실패 시 예외를 다시 발생시켜 상위 호출자에게 알림

    def _reset_state(self):
        """상태를 완전히 None으로 리셋"""
        if hasattr(self, 'resource_manager') and self.resource_manager:
            self.resource_manager.mongo_client = None
            self.resource_manager.memories = None
            self.resource_manager.vector_store = None
        self.is_initialized = False

    async def reinitialize(self):
        """MongoDB 등 연결 재시도 성공 시 전체 재초기화"""
        await self.initialize()

    async def store_memory(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        try:
            if not content or not isinstance(content, str):
                return False
            # 시스템 프롬프트/메타 메시지 필터링
            if content and (
                content.startswith("[AI CONTEXT]") or
                "EORA SYSTEM PROMPT" in content or
                "시스템 프롬프트" in content
            ):
                return False
            # 중복 저장 방지 (file_chunk 타입은 예외적으로 중복 허용)
            is_file_chunk = metadata and metadata.get('type') == 'file_chunk'
            if not is_file_chunk:
                def _db_call():
                    return self.resource_manager.memories.find_one({"content": content})
                existing = await asyncio.to_thread(_db_call)
                if existing:
                    return False
            # content/metadata.content가 벡터(리스트)면 저장하지 않음
            if isinstance(content, list):
                return False
            if metadata and isinstance(metadata.get('content'), list):
                return False
            # MemoryNode 구조 확장: 필드 누락 시 None으로 보완 (추가 필드)
            for key in [
                "user_input", "gpt_response", "emotion", "belief_tags", "event_score", "recall_priority", "emotional_intensity", "resonance_score", "intuition_vector", "timestamp", "parent_id", "memory_id",
                "fade_score", "memory_type", "source_type", "source_info", "reflex_tag", "grandparent_id", "origin_id"
            ]:
                if key not in metadata:
                    metadata[key] = None
            # reflex_tag 자동 태깅(위험/반사 단어)
            danger_words = ["위험", "욕설", "거절", "경고", "금지", "폭력"]
            if any(w in str(metadata.get("user_input", "")) for w in danger_words):
                metadata["reflex_tag"] = True
            async with self._lock:
                if not self.is_initialized:
                    return False
                if self.resource_manager is None:
                    return False
                try:
                    # content가 비어 있고 metadata에 content가 있으면 보충
                    if (not content or content == '') and metadata and 'content' in metadata:
                        content = metadata['content']
                    # 1. 의미론적 임베딩 생성
                    try:
                        embedding = await embed_text_async(content)
                    except CancelledError:
                        return False
                    except Exception as e:
                        return False
                    # 2. 메타데이터 최소화: content, user, emotion, created_at만 저장
                    minimal_metadata = {}
                    if metadata:
                        if 'user' in metadata:
                            minimal_metadata['user'] = metadata['user']
                        if 'emotion' in metadata:
                            minimal_metadata['emotion'] = metadata['emotion']
                    minimal_metadata['content'] = content
                    minimal_metadata['created_at'] = datetime.utcnow().isoformat()
                    minimal_metadata['semantic_embedding'] = embedding
                    memory = MemoryAtom(content, minimal_metadata)
                    doc = memory.to_dict()
                    # semantic_embedding을 최상위 필드로 이동
                    if 'metadata' in doc and 'semantic_embedding' in doc['metadata']:
                        doc['semantic_embedding'] = doc['metadata'].pop('semantic_embedding')
                    # content도 최상위 필드에 반드시 존재하도록 보장
                    if 'content' not in doc and 'content' in doc.get('metadata', {}):
                        doc['content'] = doc['metadata']['content']
                    # metadata에도 content, semantic_embedding이 반드시 포함되도록 보장
                    if 'metadata' in doc:
                        doc['metadata']['content'] = doc['content']
                        if 'semantic_embedding' in doc:
                            doc['metadata']['semantic_embedding'] = doc['semantic_embedding']
                    if self.resource_manager.memories is None:
                        raise RuntimeError("MongoDB 'memories' 컬렉션이 초기화되지 않았습니다.")
                    # MongoDB에 저장
                    result = await asyncio.to_thread(self.resource_manager.memories.insert_one, doc)
                    memory_id = str(result.inserted_id)
                    # Redis에 저장할 문서 사본을 만들고, _id를 문자열로 변환
                    doc_for_redis = doc.copy()
                    doc_for_redis["_id"] = memory_id
                    doc_for_redis["memory_id"] = memory_id
                    # Redis에 캐시
                    if self.resource_manager.redis_client:
                        try:
                            await self.resource_manager.redis_client.setex(
                                f"memory:{memory_id}",
                                3600,  # 1시간 TTL
                                json.dumps(doc_for_redis, cls=CustomJSONEncoder)
                            )
                        except Exception as e:
                            pass
                    return True
                except CancelledError:
                    return False
                except Exception as e:
                    return False
        except Exception as e:
            return False

    async def recall_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """메모리를 회상합니다. ObjectId 문자열 또는 일반 텍스트로 검색합니다."""
        if not self.is_initialized or not self.resource_manager or self.resource_manager.memories is None:
            await self.reinitialize()
            if not self.is_initialized or not self.resource_manager or self.resource_manager.memories is None:
                raise RuntimeError("재초기화 후에도 MongoDB 연결이 유효하지 않습니다.")

        try:
            memory = None
            # 1. key가 유효한 ObjectId 형식인지 확인
            if ObjectId.is_valid(key):
                try:
                    memory = await asyncio.to_thread(self.resource_manager.memories.find_one, {"_id": ObjectId(key)})
                except InvalidId:
                    memory = None
            # 2. ObjectId로 찾지 못했으면, metadata.key 필드에서 검색
            if memory is None:
                memory = await asyncio.to_thread(self.resource_manager.memories.find_one, {"metadata.key": key})
            # 3. 그래도 찾지 못했으면, content 필드에서 텍스트 검색
            if memory is None:
                escaped_key = re.escape(key)
                memory = await asyncio.to_thread(self.resource_manager.memories.find_one, {"content": {"$regex": escaped_key, "$options": "i"}})

            if memory:
                # _id를 문자열로 변환하여 반환
                if '_id' in memory and isinstance(memory['_id'], ObjectId):
                    memory['_id'] = str(memory['_id'])
                return memory
            return None
        except Exception as e:
            raise RuntimeError(f"메모리 회상 실패: {e}") from e

    async def search_memories_by_content(self, query: str, top_k: int = 3000) -> List[Dict[str, Any]]:
        """내용 기반으로 메모리를 검색하고 상위 K개의 결과를 반환합니다."""
        if not self.is_initialized or not self.resource_manager or self.resource_manager.memories is None:
            return []

        if not query:
            return []

        # 쿼리에서 키워드 추출 (공백 기준)
        keywords = query.split()
        if not keywords:
            return []
        
        # 각 키워드를 포함하는 OR 조건의 정규식 생성
        regex_pattern = "|".join([re.escape(k) for k in keywords])

        def _db_call():
            """데이터베이스 조회를 위한 동기 함수"""
            try:
                # 수정된 쿼리: $regex와 $or를 함께 사용
                cursor = self.resource_manager.memories.find(
                    {"content": {"$regex": regex_pattern, "$options": "i"}},
                    limit=top_k
                )
                results = [doc for doc in cursor]
                for doc in results:
                    if '_id' in doc and isinstance(doc['_id'], ObjectId):
                        doc['_id'] = str(doc['_id'])
                return results
            except Exception as e:
                logger.error(f"DB 조회 중 오류 발생 (content search): {e}", exc_info=True)
                return []

        try:
            # 동기 DB 조회를 비동기적으로 실행
            results = await asyncio.to_thread(_db_call)
            return results

        except Exception as e:
            logger.error(f"❌ 콘텐츠 기반 메모리 검색 실패: {e}", exc_info=True)
            return []

    async def search_memories_by_vector(self, query_text: str, top_k: int = 3000, distance_threshold: float = 3.0) -> List[Dict[str, Any]]:
        """
        FAISS를 사용하여 벡터 검색으로 메모리를 검색합니다.
        - 검색 결과가 임계값(distance_threshold)을 초과하면 필터링합니다.
        """
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []

        try:
            try:
                query_vector = await embed_text_async(query_text)
            except CancelledError:
                logger.warning("search_memories_by_vector에서 CancelledError 발생: 앱 종료 등으로 인한 자연스러운 현상")
                return []
            if query_vector is None or len(query_vector) == 0:
                return []
            
            # 임계값 기반 필터링을 위해 top_k보다 많은 후보군 검색
            search_k = max(top_k * 3, 20)
            if search_k > self.faiss_index.ntotal:
                search_k = self.faiss_index.ntotal

            distances, indices = self.faiss_index.search(np.array([query_vector]), search_k)
            
            # 임계값 미만인 결과만 필터링하고, 거리와 함께 저장
            filtered_results = []
            for i, dist in zip(indices[0], distances[0]):
                if i != -1 and float(dist) < distance_threshold:
                    filtered_results.append({"id": self.faiss_id_map[i], "dist": dist})

            # 상위 top_k개만 선택
            final_results = filtered_results[:top_k]

            if not final_results:
                return []

            # 검색된 ID 목록
            found_doc_ids = [res['id'] for res in final_results]

            def _db_call():
                # ObjectId로 변환 시도, 실패하면 무시
                valid_ids = []
                for doc_id in found_doc_ids:
                    try:
                        valid_ids.append(ObjectId(doc_id))
                    except (InvalidId, TypeError):
                        continue

                if not valid_ids:
                    return []
                
                # MongoDB에서 ID 목록으로 문서를 한 번에 조회
                docs = list(self.resource_manager.memories.find({"_id": {"$in": valid_ids}}))
                
                # 원래 순서를 유지하기 위해 ID를 키로 하는 딕셔너리 생성
                doc_map = {str(doc['_id']): doc for doc in docs}
                
                # found_doc_ids 순서대로 정렬된 문서 리스트 반환
                sorted_docs = [doc_map[doc_id] for doc_id in found_doc_ids if doc_id in doc_map]
                return sorted_docs

            retrieved_docs = await asyncio.to_thread(_db_call)
            
            if not retrieved_docs:
                return []

            # 안전하게 직렬화 가능한 형태로 변환
            safe_docs = [safe_mongo_doc(doc) for doc in retrieved_docs]
            
            return safe_docs
        except Exception as e:
            logger.error(f"벡터 검색 중 심각한 오류 발생: {e}", exc_info=True)
            return []

    async def safe_recall_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """키로 메모리를 안전하게 회상 (오류 발생 시 None 반환)"""
        if self.resource_manager.memories is None:
            return None
        return await self.recall_memory(key)

    def __del__(self):
        """소멸자"""
        if self.is_initialized:
            try:
                if self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(self.cleanup(), self._loop)
                else:
                    asyncio.run(self.cleanup())
            except Exception as e:
                logger.error(f"소멸자에서 정리 실패: {e}")

    async def initialize_async(self) -> None:
        """비동기 초기화 메서드"""
        if self._initialized:
            return

        try:
            # MongoDB 연결 테스트
            if not self.resource_manager.test_mongo_connection():
                raise Exception("MongoDB 연결 실패")

            # Redis 연결 테스트
            if not self.resource_manager.test_redis_connection():
                raise Exception("Redis 연결 실패")

            # 비동기 초기화 실행
            await self.resource_manager.initialize()
            
            # MongoDB 인덱스 생성
            await self._create_mongo_indexes()
            
            self._initialized = True

        except Exception as e:
            logger.error(f"❌ MemoryManager 초기화 실패: {str(e)}")
            raise

    def initialize_sync(self) -> None:
        """동기식 초기화 메서드"""
        if self._initialized:
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.initialize_async())
        finally:
            loop.close()

    async def cleanup(self):
        if hasattr(self, 'mongo_client') and self.mongo_client:
            self.mongo_client.close()
        # ... 기타 정리 코드 ...

    async def recall_recent_memories(self, limit=3000):
        """MongoDB에서 최근 메모리 N개를 반환합니다."""
        if not self.is_initialized or not self.resource_manager or self.resource_manager.memories is None:
            return []
        def _db_call():
            cursor = self.resource_manager.memories.find({}, sort=[("timestamp", -1)], limit=limit)
            results = []
            for doc in cursor:
                if '_id' in doc and isinstance(doc['_id'], ObjectId):
                    doc['_id'] = str(doc['_id'])
                results.append(doc)
            return results
        return await asyncio.to_thread(_db_call)

    async def analyze_belief_system(self, limit=20):
        """
        최근 memories로 신념/진실맵 분석
        """
        memories = await self.recall_recent_memories(limit=limit)
        return update_belief_system(memories)

    async def extract_wisdom_summary(self, limit=20):
        """
        최근 memories로 통찰/지혜 추출
        """
        memories = await self.recall_recent_memories(limit=limit)
        return extract_wisdom(memories)

    async def run_meta_cognition(self, limit=10):
        """
        최근 memories로 자기 점검/피드백 루프 실행
        """
        memories = await self.recall_recent_memories(limit=limit)
        checked = [self_check(m) for m in memories]
        feedback = self_feedback_loop(memories)
        return {'self_check': checked, 'self_feedback': feedback}

    async def check_resonance(self, limit=20):
        """
        최근 memories로 감정공명률 계산
        """
        memories = await self.recall_recent_memories(limit=limit)
        return calculate_resonance(memories)

    async def ethic_check(self, response: str, context: dict):
        """
        response/context로 윤리 필터링
        """
        return ethic_filter(response, context)

    async def search_by_metadata(self, query: dict, top_k: int = 10) -> list:
        """메타데이터 기반으로 메모리를 검색합니다."""
        if not self.is_initialized or not self.resource_manager or self.resource_manager.memories is None:
            return []
        if not query or not isinstance(query, dict):
            return []
        def _db_call():
            try:
                cursor = self.resource_manager.memories.find({
                    **{f"metadata.{k}": v for k, v in query.items()}
                }, limit=top_k)
                results = []
                for doc in cursor:
                    if '_id' in doc and isinstance(doc['_id'], ObjectId):
                        doc['_id'] = str(doc['_id'])
                    results.append(doc)
                return results
            except Exception as e:
                logger.error(f"DB 조회 중 오류 발생 (metadata search): {e}", exc_info=True)
                return []
        try:
            results = await asyncio.to_thread(_db_call)
            return results
        except Exception as e:
            logger.error(f"❌ 메타데이터 기반 메모리 검색 실패: {e}", exc_info=True)
            return []

class MemoryAtom:
    def __init__(self, content: str, metadata: Dict[str, Any] = None, **kwargs):
        """메모리 원자 초기화
        
        Args:
            content (str): 메모리 내용
            metadata (Dict[str, Any], optional): 메타데이터
            **kwargs: 추가적인 메타데이터. 'role'과 같은 키워드 인자를 메타데이터에 포함시킵니다.
        """
        self.content = content
        self.metadata = metadata or {}
        self.metadata.update(kwargs)
        self.metadata['content'] = self.content
        self.memory_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """메모리 원자를 딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 메모리 원자 딕셔너리
        """
        try:
            return {
                "content": self.content,
                "metadata": self.metadata,
                "memory_id": self.memory_id,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"메모리 직렬화 실패: {e}")
            raise

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryAtom":
        """딕셔너리에서 메모리 원자 생성
        
        Args:
            data (Dict[str, Any]): 메모리 원자 딕셔너리
            
        Returns:
            MemoryAtom: 메모리 원자 인스턴스
            
        Raises:
            ValueError: data가 유효하지 않은 경우
        """
        if not isinstance(data, dict):
            raise ValueError("data는 딕셔너리여야 합니다")
        if "content" not in data:
            raise ValueError("data에 content가 없습니다")

        try:
            instance = cls(
                content=data["content"],
                metadata=data.get("metadata", {})
            )
            
            # 메모리 ID 설정
            if "memory_id" in data:
                instance.memory_id = data["memory_id"]
            
            # 타임스탬프 설정
            try:
                instance.created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, KeyError):
                instance.created_at = datetime.utcnow()
                
            try:
                instance.updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, KeyError):
                instance.updated_at = instance.created_at
            
            return instance
        except Exception as e:
            logger.error(f"메모리 역직렬화 실패: {e}")
            raise

async def analyze_and_store_learning_material(text: str, user: str = "system") -> str:
    """
    학습자료(텍스트)를 자동 분석하여 MemoryAtom으로 저장하고, 연결 정보를 자동 생성합니다.
    """
    # 1. 감정, 신념, 중요도, 임베딩 등 분석
    emotion, emotion_score = estimate_emotion(text)
    importance = 9000 if ("핵심" in text or "중요" in text) else 8000
    try:
        embedding = embed_text(text)
    except Exception:
        embedding = None
    try:
        cognitive_layer = analyze_cognitive_layer(text)
    except Exception:
        cognitive_layer = None
    try:
        chain_id = await find_or_create_chain_id(text)
    except Exception:
        chain_id = None
    try:
        linked_ids = await find_linked_memories(text)
    except Exception:
        linked_ids = []
    
    connections_reasoned = [f"자동 분석: {cognitive_layer} 위상, 감정: {emotion}"]
    atom = MemoryAtom(
        content=text,
        metadata={
            "user": user,
            "emotion": emotion,
            "emotion_score": emotion_score,
            "importance": importance,
            "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
            "cognitive_layer": cognitive_layer,
            "chain_id": chain_id,
            "linked_ids": [m.get('memory_id') or m.get('_id') for m in linked_ids],
            "connections_reasoned": connections_reasoned,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    memory_manager = await get_memory_manager()
    await memory_manager.store_memory(content=atom.content, metadata=atom.metadata)
    return f"학습자료가 자동 분석되어 저장되었습니다. chain_id: {chain_id}, 연결: {linked_ids}" 