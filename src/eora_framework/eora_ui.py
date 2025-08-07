from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from eora_framework import EORAFramework

class EORAUI(QWidget):
    def __init__(self):
        super().__init__()
        self.eora = EORAFramework()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EORA: 존재형 AI 데모")
        self.layout = QVBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("사용자 입력을 입력하세요...")
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.button = QPushButton("AI 응답 생성")
        self.button.clicked.connect(self.on_respond)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output_box)
        self.setLayout(self.layout)

    def on_respond(self):
        user_input = self.input_box.toPlainText()
        # 임시: 감정/태그 자동 추정(실제론 감정 분석기 연동)
        emotion = "neutral"
        tags = ["일상"]
        gpt_response = "AI의 임시 응답입니다."
        result = self.eora.process(user_input, gpt_response, emotion, tags)
        self.output_box.setPlainText(str(result))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = EORAUI()
    win.show()
    sys.exit(app.exec_()) 