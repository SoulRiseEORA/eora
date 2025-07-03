
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from dotenv import dotenv_values, set_key
import os

class EORASettingsTab(QWidget):
    def __init__(self, env_path=".env"):
        super().__init__()
        self.env_path = env_path
        layout = QVBoxLayout(self)

        self.temp_label = QLabel("🔥 Temperature")
        self.temp_input = QLineEdit()
        self.model_label = QLabel("🧠 GPT 모델")
        self.model_input = QLineEdit()

        self.save_btn = QPushButton("💾 저장하기")
        self.save_btn.clicked.connect(self.save_env)

        layout.addWidget(self.temp_label)
        layout.addWidget(self.temp_input)
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_input)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        self.load_env()

    def load_env(self):
        env = dotenv_values(self.env_path)
        self.temp_input.setText(env.get("EORA_TEMPERATURE", "0.7"))
        self.model_input.setText(env.get("EORA_MODEL", "gpt-4-turbo"))

    def save_env(self):
        try:
            set_key(self.env_path, "EORA_TEMPERATURE", self.temp_input.text())
            set_key(self.env_path, "EORA_MODEL", self.model_input.text())
            QMessageBox.information(self, "저장됨", "설정이 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))
