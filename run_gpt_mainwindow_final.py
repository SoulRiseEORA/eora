import sys
import os
import logging
import inspect
import asyncio
import traceback

# ==============================================================================
# [최종 해결책] - 파이썬의 모듈 검색 경로(sys.path)에 현재 프로젝트의
#               루트 디렉토리를 강제로 추가합니다.
# ------------------------------------------------------------------------------
# 이 스크립트 파일(run_gpt_mainwindow_final.py)의 실제 경로를 가져옵니다.
this_file_path = os.path.abspath(__file__)
# 이 파일이 속한 디렉토리(프로젝트 루트)를 가져옵니다.
project_root_dir = os.path.dirname(this_file_path)

# 만약 프로젝트 루트가 sys.path에 없다면, 맨 앞에 추가합니다.
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)
    # logging.warning(f"!!! 강제 경로 추가: '{project_root_dir}' 경로를 파이썬 모듈 검색 경로에 추가했습니다.")
# ==============================================================================

# ==============================================================================
# [진단 코드] - 모듈의 실제 로딩 경로를 확인합니다.
# ------------------------------------------------------------------------------
try:
    import aura_system.recall_engine
    import ai_memory_wrapper
    import inspect

    # print("="*80)
    # print("!!! [진단] 모듈 로드 경로 검사 시작 !!!")
    # print(f"  - recall_engine: {inspect.getfile(aura_system.recall_engine)}")
    # print(f"  - ai_memory_wrapper: {inspect.getfile(ai_memory_wrapper)}")
    # print("="*80)

except ImportError as e:
    print(f"[ImportError] {e}")
    traceback.print_exc()
except Exception as e:
    print(f"[Exception] {e}")
    traceback.print_exc()
# ==============================================================================

from PyQt5.QtWidgets import QApplication
import qasync
from GPTMainWindow import GPTMainWindow
from dotenv import load_dotenv
from redis_launcher import start_redis

# 아우라 통합 시스템 import
try:
    from aura_integration import get_aura_integration, AuraIntegration
    AURA_INTEGRATION_AVAILABLE = True
    print("✅ 아우라 통합 시스템 로드 성공")
except ImportError as e:
    AURA_INTEGRATION_AVAILABLE = False
    print(f"⚠️ 아우라 통합 시스템 로드 실패: {e}")

# 기존 아우라 시스템 import (호환성)
try:
    from aura_system.memory_manager import get_memory_manager
    from aura_system.openai_client import init_openai
    from aura_system.task_manager import cleanup_pending_tasks
    AURA_SYSTEM_AVAILABLE = True
    print("✅ 기존 아우라 시스템 로드 성공")
except ImportError as e:
    AURA_SYSTEM_AVAILABLE = False
    print(f"⚠️ 기존 아우라 시스템 로드 실패: {e}")

# 로깅 설정
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(name)s: %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('aura_system.log')
#     ]
# )

async def main():
    """애플리케이션의 메인 비동기 진입점"""
    # logging.info("🚀 앱 시작")

    try:
        start_redis()
        # logging.info("✅ Redis 서버 시작됨")
    except Exception as e:
        print(f"[Redis Error] {e}")
        traceback.print_exc()

    # 아우라 통합 시스템 초기화
    aura_integration = None
    if AURA_INTEGRATION_AVAILABLE:
        try:
            aura_integration = await get_aura_integration()
            if not aura_integration or not aura_integration._initialized:
                raise RuntimeError("아우라 통합 시스템 초기화에 실패했습니다.")
            print("✅ 아우라 통합 시스템 초기화 완료")
        except Exception as e:
            print(f"[Aura Integration Error] {e}")
            traceback.print_exc()
            aura_integration = None

    # 기존 아우라 시스템 초기화 (폴백)
    memory_manager = None
    if not aura_integration and AURA_SYSTEM_AVAILABLE:
        try:
            memory_manager = await get_memory_manager()
            if not memory_manager or not memory_manager.is_initialized:
                raise RuntimeError("메모리 매니저 초기화에 실패했지만 예외가 발생하지 않았습니다.")
            print("✅ 기존 메모리 매니저 초기화 완료")
        except Exception as e:
            print(f"[MemoryManager Error] {e}")
            traceback.print_exc()
            return

    # OpenAI 초기화
    if AURA_SYSTEM_AVAILABLE:
        try:
            init_openai()
            print("✅ OpenAI 초기화 완료")
        except Exception as e:
            print(f"[OpenAI Error] {e}")
            traceback.print_exc()

    app = QApplication.instance() or QApplication(sys.argv)
    
    # 아우라 통합 시스템을 우선적으로 사용
    if aura_integration:
        window = GPTMainWindow(aura_integration=aura_integration)
        print("✅ GPTMainWindow 실행됨 (아우라 통합 시스템 사용)")
    else:
        window = GPTMainWindow(memory_manager=memory_manager)
        print("✅ GPTMainWindow 실행됨 (기존 시스템 사용)")
    
    shutdown_future = asyncio.get_event_loop().create_future()
    window.set_shutdown_future(shutdown_future)
    window.show()
    # logging.info("✅ GPTMainWindow 실행됨.")

    await shutdown_future

    # logging.info("애플리케이션 종료 신호 수신. 정리 작업을 시작합니다.")
    
    # 아우라 통합 시스템 정리
    if aura_integration:
        try:
            await aura_integration.cleanup()
            print("✅ 아우라 통합 시스템 정리 완료")
        except Exception as e:
            print(f"[Aura Integration Cleanup Error] {e}")
    
    # 기존 시스템 정리
    if AURA_SYSTEM_AVAILABLE:
        try:
            await cleanup_pending_tasks()
            print("✅ 기존 시스템 정리 완료")
        except Exception as e:
            print(f"[Cleanup Error] {e}")
    
    # logging.info("모든 정리 작업 완료. 앱을 완전히 종료합니다.")

if __name__ == "__main__":
    load_dotenv()
    app_base_dir = os.path.dirname(os.path.abspath(__file__))
    chat_logs_dir = os.path.join(app_base_dir, "chat_logs")
    os.makedirs(chat_logs_dir, exist_ok=True)
    # logging.info(f"채팅 로그 디렉토리 준비됨: {chat_logs_dir}")

    try:
        qasync.run(main())
    except asyncio.CancelledError:
        print("👋 앱 종료 (이벤트 루프 취소됨)")
    except Exception as e:
        print(f"[Main Exception] {e}")
        traceback.print_exc()