
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget,
    QTextEdit, QPushButton, QListWidgetItem, QMessageBox
)
import json
import os

PROMPT_DB = "ai_prompts.json"

class AIManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.ai_names = ["ai0", "ai1", "ai2", "ai3", "ai4", "ai5"]
        self.prompts = self.load_prompts()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.selector = QComboBox()
        self.selector.addItems(self.ai_names)
        self.selector.currentTextChanged.connect(self.show_prompts)

        self.prompt_list = QListWidget()

        self.role_input = QTextEdit(); self.role_input.setPlaceholderText("🧠 역할/정체성")
        self.guide_input = QTextEdit(); self.guide_input.setPlaceholderText("📘 지침/규칙")
        self.etc_input = QTextEdit(); self.etc_input.setPlaceholderText("🧾 기타 프롬프트")
        for box in [self.role_input, self.guide_input, self.etc_input]:
            box.setFixedHeight(60)

        self.btn_add = QPushButton("➕ 등록")
        self.btn_add.clicked.connect(self.add_prompt)

        self.btn_del = QPushButton("🗑️ 선택 삭제")
        self.btn_del.clicked.connect(self.delete_prompt)

        layout.addWidget(QLabel("🤖 AI 선택"))
        layout.addWidget(self.selector)
        layout.addWidget(QLabel("📋 현재 프롬프트 목록"))
        layout.addWidget(self.prompt_list)
        layout.addWidget(self.role_input)
        layout.addWidget(self.guide_input)
        layout.addWidget(self.etc_input)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_del)

        self.show_prompts(self.ai_names[0])

    def load_prompts(self):
        if os.path.exists(PROMPT_DB):
            with open(PROMPT_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        return {name: [] for name in self.ai_names}

    def show_prompts(self, ai_name):
        self.prompt_list.clear()
        for p in self.prompts.get(ai_name, []):
            self.prompt_list.addItem(p)

    def add_prompt(self):
        ai = self.selector.currentText()
        lines = []
        if self.role_input.toPlainText().strip():
            lines.append("[정체성] " + self.role_input.toPlainText().strip())
        if self.guide_input.toPlainText().strip():
            lines.append("[지침] " + self.guide_input.toPlainText().strip())
        if self.etc_input.toPlainText().strip():
            lines.append("[기타] " + self.etc_input.toPlainText().strip())
        if not lines:
            return
        for line in lines:
            self.prompts.setdefault(ai, []).append(line)
            self.prompt_list.addItem(line)
        self.save()
        self.role_input.clear(); self.guide_input.clear(); self.etc_input.clear()

    def delete_prompt(self):
        row = self.prompt_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "삭제 실패", "삭제할 프롬프트를 선택하세요.")
            return
        text = self.prompt_list.currentItem().text()
        ai = self.selector.currentText()
        self.prompts[ai].remove(text)
        self.prompt_list.takeItem(row)
        self.save()

    def save(self):
        with open(PROMPT_DB, "w", encoding="utf-8") as f:
            json.dump(self.prompts, f, indent=2, ensure_ascii=False)
