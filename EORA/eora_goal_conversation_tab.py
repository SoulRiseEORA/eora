
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QListWidget, QLineEdit, QLabel
import datetime

class EORAGoalPlannerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.goal_list = QListWidget()
        self.eora_message = QTextEdit()
        self.eora_message.setPlaceholderText("📌 이오라가 제안한 목표, 질문, 코멘트 등")
        self.eora_message.setReadOnly(True)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("👤 사용자 응답 또는 지시 입력")
        self.reply_btn = QPushButton("📤 전송")

        self.generate_btn = QPushButton("🧠 이오라 목표 자동 생성")
        self.generate_btn.clicked.connect(self.generate_goal)
        self.reply_btn.clicked.connect(self.user_reply)

        self.layout.addWidget(QLabel("🎯 이오라의 목표 목록"))
        self.layout.addWidget(self.goal_list)
        self.layout.addWidget(self.generate_btn)
        self.layout.addWidget(QLabel("🧠 이오라의 질문 / 코멘트"))
        self.layout.addWidget(self.eora_message)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.reply_btn)

        self.setLayout(self.layout)

    def generate_goal(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        suggestion = f"[{now}] 'AI를 활용한 사용자 문맥 자동 요약 기능 설계'"
        self.goal_list.addItem(suggestion)
        message = "이오라 제안 목표:\n" + suggestion + "\n이 목표를 시작해도 괜찮을까요?"
        self.eora_message.setPlainText(message)

    def user_reply(self):
        text = self.user_input.text().strip()
        if text:
            self.eora_message.append(f"\n👤 사용자: {text}")
            self.user_input.clear()
