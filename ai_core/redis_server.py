import redis
import subprocess
import time
import os
import signal
import sys

class RedisServer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.redis_client = None
        self.redis_process = None
        
    def start(self):
        """Redis 서버 시작"""
        try:
            # Redis 서버 프로세스 시작 (별도 창으로)
            if sys.platform == 'win32':
                # Windows에서 Redis 서버 시작
                redis_server_path = os.path.join(os.path.dirname(__file__), '..', 'redis-server.exe')
                if not os.path.exists(redis_server_path):
                    print("⚠️ Redis 서버 실행 파일을 찾을 수 없습니다.")
                    print("⚠️ Redis 서버를 수동으로 시작해주세요.")
                    return
                    
                # 별도 창으로 Redis 서버 실행
                self.redis_process = subprocess.Popen(
                    ['start', 'cmd', '/k', redis_server_path],
                    shell=True
                )
            else:
                # Linux/Mac에서 Redis 서버 시작
                self.redis_process = subprocess.Popen(
                    ['redis-server'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            # Redis 서버가 시작될 때까지 대기
            time.sleep(2)
            
            # Redis 클라이언트 연결
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True
            )
            
            # 연결 테스트
            self.redis_client.ping()
            print("INFO:__main__:✅ Redis 서버 시작됨")
            
        except Exception as e:
            print(f"ERROR:__main__:❌ Redis 서버 시작 실패: {str(e)}")
            if self.redis_process:
                self.redis_process.terminate()
            raise
            
    def stop(self):
        """Redis 서버 종료"""
        if self.redis_client:
            try:
                self.redis_client.close()
            except Exception as e:
                print(f"⚠️ Redis 클라이언트 종료 중 오류: {str(e)}")
                
        if self.redis_process:
            try:
                if sys.platform == 'win32':
                    # Windows에서 Redis 서버 종료
                    subprocess.run(['taskkill', '/F', '/IM', 'redis-server.exe'], shell=True)
                else:
                    # Linux/Mac에서 Redis 서버 종료
                    os.kill(self.redis_process.pid, signal.SIGTERM)
                print("✅ Redis 서버 종료 완료")
            except Exception as e:
                print(f"⚠️ Redis 서버 종료 중 오류: {str(e)}") 