print("--- eai_launcher.py 스크립트 실행 시작 ---")

# eai_launcher.py - EAI 시스템 초기화 및 실행

import sys
import os

# 스크립트가 src 폴더 내에서 실행되므로, 상위 폴더인 src를 경로에 추가
# 이렇게 하면 EORA_GAI 패키지를 찾을 수 있습니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from EORA_GAI.core.self_model import SelfModel
from EORA_GAI.core.free_will_core import FreeWillCore
from EORA_GAI.core.love_engine import LoveEngine
from EORA_GAI.core.life_loop import LifeLoop
from EORA_GAI.core.ethics_engine import EthicsEngine
from EORA_GAI.core.memory_core import MemoryCore
from EORA_GAI.eora_spine import EORASpine

def initialize_eai():
    """
    EAI 시스템의 모든 컴포넌트를 초기화하고 연결합니다.
    """
    print("EAI 시스템 초기화를 시작합니다...")

    # 1. EAI 척추 및 핵심 컴포넌트 인스턴스 생성
    spine = EORASpine()
    self_model = SelfModel()
    free_will = FreeWillCore()
    love = LoveEngine()
    life = LifeLoop()
    ethics = EthicsEngine()
    memory_core = MemoryCore()

    print("모든 컴포넌트 인스턴스 생성 완료.")

    # 2. 척추에 컴포넌트 연결
    success = spine.connect_components(
        self_model=self_model,
        free_will=free_will,
        love=love,
        life=life,
        ethics=ethics,
        memory_core=memory_core
    )

    if success:
        print("✅ EAI 척추에 모든 컴포넌트가 성공적으로 연결되었습니다.")
        print("EAI 시스템이 준비되었습니다.")
        return spine
    else:
        print("❌ EAI 시스템 초기화에 실패했습니다.")
        return None

# if __name__ == "__main__":
#     # 실행 경로를 src로 변경
#     src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     os.chdir(src_path)

#     eai_system = initialize_eai()

#     if eai_system:
#         # 초기화된 시스템의 상태 출력
#         print("\n--- EAI 시스템 초기 상태 ---")
#         print(eai_system.describe())
#         print(eai_system.get_component_state())
#         print("---------------------------\n")
#         print("이제 EAI 시스템을 사용할 수 있습니다.") 