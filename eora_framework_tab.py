from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from aura_system.ai_chat import get_eora_ai
from aura_system.memory_manager import get_memory_manager
import asyncio
import qasync # qasync 임포트

class EORAFrameworkTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.eora_ai = None
        self.memory_manager = None
        self.init_ui()
        # __init__에서는 비동기 호출을 하지 않습니다.

    def init_ui(self):
        self.setWindowTitle("EORA: 존재형 AI 프레임워크")
        layout = QVBoxLayout(self)

        self.input_label = QLabel("사용자 입력:")
        layout.addWidget(self.input_label)
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("사용자 입력을 입력하고 'EORA 처리' 버튼을 누르세요...")
        layout.addWidget(self.input_box)

        self.button = QPushButton("EORA 처리 (초기화 중...)")
        self.button.setEnabled(False) # 초기에는 비활성화
        # qasync.asyncSlot을 사용하여 비동기 메서드를 연결합니다.
        self.button.clicked.connect(qasync.asyncSlot(self.on_process))
        layout.addWidget(self.button)

        self.output_label = QLabel("EORA 분석 결과:")
        layout.addWidget(self.output_label)
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

    async def initialize_ai(self):
        """AI 시스템을 비동기적으로 초기화합니다."""
        try:
            self.memory_manager = await get_memory_manager()
            self.eora_ai = await get_eora_ai(self.memory_manager)
            self.button.setText("EORA 처리")
            self.button.setEnabled(True)
            print("EORA AI가 성공적으로 초기화되었습니다.")
        except Exception as e:
            self.output_box.setPlainText(f"AI 초기화 오류 발생:\n{e}")
            print(f"EORA AI 초기화 실패: {e}")

    @qasync.asyncSlot()
    async def on_process(self):
        user_input = self.input_box.toPlainText()
        if not user_input:
            self.output_box.setPlainText("입력값이 없습니다.")
            return
        
        if self.eora_ai is None:
            self.output_box.setPlainText("AI가 아직 초기화되지 않았습니다. 잠시 후 다시 시도해주세요.")
            return

        self.output_box.setPlainText("EORA 처리 중...")
        self.button.setEnabled(False)
        try:
            # 이제 on_process가 비동기 함수이므로 await를 직접 사용할 수 있습니다.
            result = await self.eora_ai.respond_async(user_input)
            
            response_text = result.get("response", "응답 없음")
            analysis = result.get("analysis", {})
            
            formatted_result = f"## EORA 응답 ##\n{response_text}\n\n## 분석 결과 ##\n"
            for key, value in analysis.items():
                # value가 복잡한 객체일 수 있으므로 str()로 변환
                formatted_result += f"📌 {key}:\n{str(value)}\n\n"
            
            self.output_box.setPlainText(formatted_result)
        except Exception as e:
            self.output_box.setPlainText(f"오류 발생:\n{e}")
        finally:
            self.button.setEnabled(True) 