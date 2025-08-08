import subprocess
import os
import threading
import signal
import psutil
import time
import atexit
from aura_system.logger import logger

class RedisLauncher:
    _instance = None
    _process = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._process = None
        self._redis_path = self._find_redis_server()
        self._config_path = self._find_redis_config()

    def _find_redis_server(self) -> str:
        """Redis 서버 실행 파일을 찾습니다."""
        # 1. 현재 디렉토리 확인
        current_dir = os.path.dirname(__file__)
        redis_path = os.path.join(current_dir, "redis-server.exe")
        if os.path.exists(redis_path):
            return redis_path
        
        # 2. 기본 설치 경로 확인
        default_path = os.path.join("C:\\Program Files\\Redis", "redis-server.exe")
        if os.path.exists(default_path):
            return default_path
        
        raise FileNotFoundError("redis-server.exe를 찾을 수 없습니다. Redis가 설치되어 있는지 확인해주세요.")

    def _find_redis_config(self) -> str:
        """Redis 설정 파일을 찾습니다."""
        config_path = os.path.join(os.path.dirname(__file__), "redis.windows.conf")
        if os.path.exists(config_path):
            return config_path
        return None

    def _is_redis_running(self) -> bool:
        """Redis 서버가 실행 중인지 확인합니다."""
        for proc in psutil.process_iter(['pid', 'name']):
            if 'redis-server' in proc.info['name'].lower():
                return True
        return False

    def start(self):
        """Redis 서버를 시작합니다."""
        if self._is_redis_running():
            logger.info("✅ Redis 서버가 이미 실행 중입니다.")
            return

        try:
            args = [self._redis_path]
            if self._config_path:
                args.append(self._config_path)

            self._process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            # 서버 시작 대기
            for _ in range(10):  # 최대 10초 대기
                if self._is_redis_running():
                    logger.info("✅ Redis 서버 시작됨")
                    return
                time.sleep(1)

            raise TimeoutError("Redis 서버 시작 시간 초과")

        except Exception as e:
            logger.error(f"❌ Redis 서버 시작 실패: {e}")
            self.stop()  # 실패 시 정리
            raise

    def stop(self):
        """Redis 서버를 종료합니다."""
        if not self._process:
            return

        try:
            if psutil.pid_exists(self._process.pid):
                parent = psutil.Process(self._process.pid)
                children = parent.children(recursive=True)
                
                # 자식 프로세스 종료
                for child in children:
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                
                # 부모 프로세스 종료
                try:
                    parent.terminate()
                    # 프로세스가 종료될 때까지 최대 3초 대기
                    parent.wait(timeout=3)
                except psutil.NoSuchProcess:
                    pass
                except psutil.TimeoutExpired:
                    # 강제 종료
                    try:
                        parent.kill()
                    except psutil.NoSuchProcess:
                        pass
                
                logger.info("✅ Redis 서버 종료됨")
            else:
                logger.info("ℹ️ Redis 서버가 이미 종료됨")

        except Exception as e:
            logger.error(f"❌ Redis 서버 종료 실패: {e}")
        finally:
            self._process = None

    def __del__(self):
        """소멸자에서 Redis 서버를 종료합니다."""
        self.stop()

# 전역 인스턴스
_launcher = None

def get_launcher() -> RedisLauncher:
    global _launcher
    if _launcher is None:
        _launcher = RedisLauncher.get_instance()
    return _launcher

def start_redis():
    """Redis 서버를 시작합니다."""
    get_launcher().start()

def stop_redis():
    """Redis 서버를 종료합니다."""
    get_launcher().stop()

# 프로그램 종료 시 Redis 서버 종료
atexit.register(stop_redis) 