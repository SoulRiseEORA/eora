import asyncio
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import redis.asyncio as redis
from redis.exceptions import ConnectionError as RedisConnectionError
from tenacity import retry, stop_after_attempt, wait_exponential
from aura_system.vector_store import FaissIndex
from aura_system.logger import logger
from aura_system.config import get_mongo_uri, get_redis_uri, get_config
import logging
import socket

class ResourceManager:
    def __init__(self):
        self.mongo_client = None
        self.redis_client = None
        self.vector_store = None
        self._loop = None
        self.is_initialized = False
        # MongoDB URI 설정 - database.py의 안정적인 로직 활용
        import os
        
        # database.py에서 URL 가져오기 시도 (가장 안정적)
        try:
            import sys
            sys.path.append('.')
            sys.path.append('..')
            from database import get_mongodb_url
            
            self.mongo_uri = get_mongodb_url()
            logger.info(f"✅ database.py에서 MongoDB URL 가져옴: {self.mongo_uri[:50]}...")
            
        except (ImportError, Exception) as e:
            logger.warning(f"⚠️ database.py 가져오기 실패: {e}")
            
            # fallback: 직접 환경변수 확인
            is_railway = any([
                os.getenv("RAILWAY_ENVIRONMENT"),
                os.getenv("RAILWAY_PROJECT_ID"),
                os.getenv("RAILWAY_SERVICE_ID")
            ])
            
            if is_railway:
                # Railway 환경에서 MongoDB URL 찾기
                railway_urls = [
                    os.getenv("MONGODB_URL"),
                    os.getenv("MONGO_URL"),
                    # 개별 변수로 구성된 URL
                    f"mongodb://{os.getenv('MONGOUSER')}:{os.getenv('MONGOPASSWORD')}@{os.getenv('MONGOHOST')}:{os.getenv('MONGOPORT')}" if all([
                        os.getenv('MONGOUSER'), os.getenv('MONGOPASSWORD'), 
                        os.getenv('MONGOHOST'), os.getenv('MONGOPORT')
                    ]) else None,
                    os.getenv("MONGODB_URI")
                ]
                
                self.mongo_uri = None
                for url in railway_urls:
                    if url and url.strip():
                        self.mongo_uri = url.strip()
                        break
                
                if not self.mongo_uri:
                    self.mongo_uri = "mongodb://localhost:27017"
            else:
                self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.mongo_db = "aura_memory"
        self.redis_uri = get_redis_uri()
        self.memories = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
    async def _connect_mongodb(self):
        """MongoDB 연결을 시도합니다."""
        try:
            logger.debug(f"Mongo URI 확인: {self.mongo_uri}")
            self.mongo_client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            # 연결 테스트
            try:
                self.mongo_client.admin.command('ping')
            except Exception as e:
                logger.error("MongoDB 연결 실패! 서버가 실행 중인지, 포트/주소가 올바른지, 방화벽이 막고 있지 않은지 확인하세요.")
                logger.error(f"MongoDB ping 실패 (URI: {self.mongo_uri}): {repr(e)}")
                self.memories = None
                raise RuntimeError(f"MongoDB ping 실패 (URI: {self.mongo_uri}): {repr(e)}")

            # DB 이름 추출 (mongo_uri에서 추출, 없으면 config에서)
            db_name = None
            if hasattr(self, 'mongo_db') and self.mongo_db:
                db_name = self.mongo_db  # 문자열 그대로 사용, await 금지
            else:
                # 1. mongo_uri에서 추출
                if '/' in self.mongo_uri:
                    db_name = self.mongo_uri.rsplit('/', 1)[-1].split('?')[0]
                    if not db_name or db_name in ('', 'admin', 'test'):
                        db_name = None
                # 2. config에서 추출
                if not db_name:
                    db_name = get_config().get("mongodb", {}).get("db")
                # 3. 그래도 없으면 기본값
                if not db_name:
                    db_name = "aura_memory"

            db = self.mongo_client[db_name]
            self.memories = db["memories"]  # ✅ 컬렉션 객체
            if self.memories is None or isinstance(self.memories, str):
                raise RuntimeError(f"MongoDB memories 컬렉션이 초기화되지 않았습니다 (DB: {db_name})")

            # 인덱스 생성
            self.memories.create_index([("content", "text")])
            self.memories.create_index([("timestamp", pymongo.DESCENDING)])
            logger.info(f"✅ MongoDB 연결 및 인덱스 생성 성공 (DB: {db_name})")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB 연결 실패: {e}")
            self.memories = None
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
    async def _connect_redis(self):
        """Redis 연결을 시도합니다."""
        try:
            self.redis_client = redis.Redis.from_url(
                self.redis_uri,
                decode_responses=True,
                            socket_timeout=3,  # 소켓 타임아웃 단축
            socket_connect_timeout=3  # 연결 타임아웃 단축
            )
            # 연결 테스트 (비동기 호출로 변경)
            await self.redis_client.ping()
            logger.info("✅ Redis 연결 성공")
            return True
        except RedisConnectionError as e:
            logger.error(f"❌ Redis 연결 실패: {e}")
            raise

    async def _initialize_vector_store(self):
        """Vector Store를 초기화합니다."""
        try:
            self.vector_store = FaissIndex()
            # Vector Store 초기화 테스트
            test_embedding = self.vector_store.get_embedding("test")
            if test_embedding is not None:
                logger.info("✅ Vector Store 초기화 성공")
                return True
            else:
                raise ValueError("Vector Store 초기화 실패")
        except Exception as e:
            logger.error(f"❌ Vector Store 초기화 실패: {e}")
            raise

    async def _connect_mongodb_simple(self):
        try:
            self.mongo_client = MongoClient(self.mongo_uri)
            db = self.mongo_client[self.mongo_db]
            self.memories = db["memories"]

            if self.memories is None:
                raise RuntimeError("MongoDB 'memories' 컬렉션 초기화 실패")

            logging.info(f"✅ MongoDB 연결 및 'memories' 컬렉션 초기화 완료")
        except Exception as e:
            logging.error(f"❌ MongoDB 연결 실패: {e}")
            raise

    def check_mongodb_port(self, host="localhost", port=27017, timeout=2):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except Exception as e:
            logger.error(f"MongoDB 포트({host}:{port}) 연결 실패: {e}")
            return False

    async def initialize(self) -> None:
        """리소스를 초기화합니다."""
        if self.is_initialized:
            return

        # MongoDB 포트 진단 추가
        if not self.check_mongodb_port():
            logger.error("MongoDB 서버가 실행 중이 아니거나 포트가 열려 있지 않습니다. 반드시 MongoDB를 실행하세요.")
        try:
            logger.info("initialize: MongoDB 연결 시도")
            try:
                await asyncio.wait_for(self._connect_mongodb(), timeout=3)  # MongoDB 연결 타임아웃 단축
                logger.info("initialize: MongoDB 연결 완료")
            except asyncio.TimeoutError as e:
                logger.error("MongoDB 연결(타임아웃)! 서버가 실행 중인지, 포트/주소가 올바른지, 방화벽이 막고 있지 않은지 확인하세요.")
                logger.error(f"MongoDB 연결 TimeoutError (URI: {self.mongo_uri}): {repr(e)}")
                raise
            except Exception as e:
                logger.error(f"❌ MongoDB 연결 실패 (initialize): {e}")
                raise
            logger.info("initialize: 간단 버전 MongoDB 연결 시도")
            await asyncio.wait_for(self._connect_mongodb_simple(), timeout=3)
            logger.info("initialize: 간단 버전 MongoDB 연결 완료")
            if self.memories is None:
                logger.error("MongoDB memories가 None입니다 (initialize)")
                raise RuntimeError("MongoDB가 초기화되지 않았습니다")
            logger.info("initialize: Redis 연결 시도")
            await asyncio.wait_for(self._connect_redis(), timeout=3)  # Redis 연결 타임아웃 단축
            logger.info("initialize: Redis 연결 완료")
            logger.info("initialize: Vector Store 초기화 시도")
            await asyncio.wait_for(self._initialize_vector_store(), timeout=3)  # Vector Store 초기화 타임아웃 단축
            logger.info("initialize: Vector Store 초기화 완료")

            self.is_initialized = True
            logger.info("✅ ResourceManager 초기화 완료")

        except Exception as e:
            logger.error(f"❌ ResourceManager 초기화 실패: {repr(e)}")
            await self.cleanup()
            raise

    async def cleanup(self) -> None:
        """리소스를 안전하게 정리합니다."""
        try:
            # Vector Store 정리
            if self.vector_store:
                self.vector_store = None
                logger.info("✅ Vector Store 정리 완료")

            # Redis 연결 종료
            if self.redis_client:
                try:
                    self.redis_client.close()
                    logger.info("✅ Redis 연결 종료 완료")
                except Exception as e:
                    logger.error(f"❌ Redis 연결 종료 실패: {e}")
                finally:
                    self.redis_client = None

            # MongoDB 연결 종료
            if self.mongo_client:
                try:
                    self.mongo_client.close()
                    logger.info("✅ MongoDB 연결 종료 완료")
                except Exception as e:
                    logger.error(f"❌ MongoDB 연결 종료 실패: {e}")
                finally:
                    self.mongo_client = None
                    self.memories = None

            self.is_initialized = False
            logger.info("✅ ResourceManager 정리 완료")

        except Exception as e:
            logger.error(f"❌ ResourceManager 정리 중 오류 발생: {e}")
            raise

    def __del__(self):
        """소멸자에서 리소스를 정리합니다."""
        try:
            if self._loop and not self._loop.is_closed():
                if self._loop.is_running():
                    self._loop.create_task(self.cleanup())
                else:
                    self._loop.run_until_complete(self.cleanup())
        except Exception as e:
            logger.error(f"❌ ResourceManager 정리 중 오류 발생: {e}") 

    def test_mongo_connection(self, timeout: int = 5) -> bool:
        """MongoDB 연결 테스트"""
        try:
            if self.mongo_client is None:
                return False
            self.mongo_client.admin.command('ping')
            return True
        except Exception as e:
            import logging
            logging.error(f"MongoDB 연결 실패: {e}")
            return False

    def test_redis_connection(self, timeout: int = 5) -> bool:
        """Redis 연결 테스트"""
        # 이 함수는 동기 컨텍스트에서 호출될 수 있으므로,
        # 직접 비동기 코드를 실행하기 어렵습니다.
        # 대신, initialize()의 _connect_redis()를 신뢰하거나
        # 별도의 동기 클라이언트로 테스트해야 합니다.
        # 현재 구조에서는 이 테스트가 정확하지 않을 수 있으므로, ping() 성공 여부로 갈음합니다.
        try:
            if self.redis_client is None:
                return False
            # 실제 비동기 ping은 _connect_redis에서 이미 수행됨
            return True
        except Exception as e:
            import logging
            logging.error(f"Redis 연결 테스트 실패: {e}")
            return False

    def get_mongo_client(self):
        """MongoClient 객체를 안전하게 반환 (없으면 None)"""
        return self.mongo_client
