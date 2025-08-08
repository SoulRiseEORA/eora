import os
import sys
import asyncio
from dotenv import load_dotenv
from memory_manager import MemoryManagerAsync as MemoryManager
from ai_chat import get_eora_instance
from monitoring import start_metrics_server
from PyQt5.QtWidgets import QApplication
from GPTMainWindow import GPTMainWindow

# ✅ 전역 asyncio 루프를 생성 (한 번만)
global_event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(global_event_loop)

def main():
    # ✅ 환경 변수 로드
    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    REDIS_URI = os.getenv("REDIS_URI", "redis://127.0.0.1:6379/0")
    print("🔄 Loaded .env from:", os.getcwd() + "/.env")
    print("✅ OpenAI API 키 로드 완료")

    # ✅ Prometheus 모니터링 서버 실행
    start_metrics_server()

    # ✅ 메모리 매니저 초기화
    mem_mgr = MemoryManager(mongo_uri=MONGO_URI, redis_uri=REDIS_URI)
    print("✅ MemoryManager 생성 완료")

    # ✅ EORA 인스턴스 불러오기
    eora_instance = get_eora_instance(memory_manager=mem_mgr)
    print("✅ EORA 인스턴스 로딩 완료")

    # ✅ PyQt 앱 실행
    app = QApplication(sys.argv)
    main_window = GPTMainWindow(memory_manager=mem_mgr, eora=eora_instance, event_loop=global_event_loop)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
