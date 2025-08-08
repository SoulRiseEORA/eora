import subprocess
import os
import signal
import psutil
import atexit

redis_process = None

def find_redis_server():
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

def start_redis():
    global redis_process
    try:
        redis_path = find_redis_server()
        redis_conf = os.path.join(os.path.dirname(__file__), "redis.windows.conf")
        args = [redis_path]
        if os.path.exists(redis_conf):
            args.append(redis_conf)
        redis_process = subprocess.Popen(
            args,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("✅ Redis 서버 시작됨 (새 창)")
    except Exception as e:
        print(f"❌ Redis 실행 실패: {e}")
        raise

def stop_redis():
    global redis_process
    if redis_process:
        try:
            # 프로세스가 여전히 실행 중인지 확인
            if psutil.pid_exists(redis_process.pid):
                parent = psutil.Process(redis_process.pid)
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
                
                print("✅ Redis 서버 종료됨")
            else:
                print("ℹ️ Redis 서버가 이미 종료됨")
        except Exception as e:
            print(f"❌ Redis 종료 실패: {e}")
        finally:
            redis_process = None

atexit.register(stop_redis) 