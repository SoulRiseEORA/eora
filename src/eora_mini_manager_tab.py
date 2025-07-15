from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt
from EORA_GAI.gpt_eora_pipeline import GPT_EORA_Pipeline

class EORAMiniManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.pipeline = GPT_EORA_Pipeline()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title = QLabel("🧠 이오라 코어 - 철학 응답 + 감정 판단 + 판단 기록")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.response_log = QTextBrowser()
        self.response_log.setReadOnly(True)
        layout.addWidget(self.response_log)

        # 입력 + 버튼 + 지우기
        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("메시지를 입력하고 Enter 또는 ▶ 버튼을 누르세요.")
        self.input_box.returnPressed.connect(self.handle_input)

        self.send_button = QPushButton("▶")
        self.send_button.clicked.connect(self.handle_input)

        self.clear_button = QPushButton("🧹 지우기")
        self.clear_button.clicked.connect(self.response_log.clear)

        input_row.addWidget(self.input_box)
        input_row.addWidget(self.send_button)
        input_row.addWidget(self.clear_button)
        layout.addLayout(input_row)

    def handle_input(self):
        user_input = self.input_box.text().strip()
        if not user_input:
            self.response_log.append("<i>⚠️ 입력이 비어 있습니다.</i>")
            return
        self.input_box.clear()

        try:
            result = self.pipeline.run(user_input)

            self.response_log.append(f"<b>👤 당신:</b> {result.get('user_input', '')}")
            self.response_log.append(f"<b>🧠 EORA 응답:</b> {result.get('eora_response', '')}")
            self.response_log.append(f"<b>💫 MiniAI 판단:</b> {result.get('mini_response', '')}")
            self.response_log.append(f"<b>📊 감정 진폭:</b> {result.get('emotion_level', '')}")
            self.response_log.append(f"<b>⚖️ 최종 판단:</b> {result.get('final_judgment', '')}")
            self.response_log.append("<hr>")
        except Exception as e:
            self.response_log.append(f"<b>❌ 오류 발생:</b> {str(e)}")