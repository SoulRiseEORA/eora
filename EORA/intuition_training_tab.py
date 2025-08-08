
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt
from aura_system.intuition_engine import run_ir_core_prediction

class IntuitionTrainingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.is_training = False

    def init_ui(self):
        layout = QVBoxLayout()

        self.info_label = QLabel("💡 직감 훈련 탭입니다. 메시지를 입력하고 직감 판단을 확인하세요.")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.start_button = QPushButton("훈련 시작")
        self.start_button.clicked.connect(self.toggle_training)
        layout.addWidget(self.start_button)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("훈련 메시지를 입력하세요...")
        layout.addWidget(self.message_input)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        layout.addWidget(self.result_output)

        self.setLayout(layout)

    def toggle_training(self):
        if not self.is_training:
            self.is_training = True
            self.start_button.setText("훈련 중지")
            self.run_training()
        else:
            self.is_training = False
            self.start_button.setText("훈련 시작")

    def run_training(self):
        if not self.is_training:
            return
        message = self.message_input.toPlainText().strip()
        if message:
            result = run_ir_core_prediction()
            log = f"[입력] {message}\n[직감] {result}\n\n"
            self.result_output.append(log)
            with open("training_log.txt", "a", encoding="utf-8") as f:
                f.write(log)
        else:
            self.result_output.append("⚠️ 입력된 메시지가 없습니다.")
