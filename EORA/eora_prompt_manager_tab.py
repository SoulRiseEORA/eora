
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QComboBox, QFileDialog
import json, os

class EORAPromptManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.path = "./ai_brain/ai_prompts.json"
        self.selected_role = "ai1"
        self.selected_type = "system"

        self.info_label = QLabel("📘 프롬프트 매니저 (ai_prompts.json)")
        self.layout.addWidget(self.info_label)

        self.selector_layout = QHBoxLayout()
        self.role_box = QComboBox()
        self.role_box.addItems(["ai1", "ai2", "ai3", "ai4", "ai5", "ai6"])
        self.role_box.currentTextChanged.connect(self.set_role)

        self.type_box = QComboBox()
        self.type_box.addItems(["system", "guide", "role", "debug", "format"])
        self.type_box.currentTextChanged.connect(self.set_type)

        self.selector_layout.addWidget(QLabel("🎯 대상 AI:"))
        self.selector_layout.addWidget(self.role_box)
        self.selector_layout.addWidget(QLabel("🧠 프롬프트 타입:"))
        self.selector_layout.addWidget(self.type_box)
        self.layout.addLayout(self.selector_layout)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("✏️ 새로운 프롬프트를 입력하거나 기존 내용을 수정하세요.")
        self.layout.addWidget(self.prompt_input)

        self.buttons_layout = QHBoxLayout()
        self.load_btn = QPushButton("📂 불러오기")
        self.load_btn.clicked.connect(self.load_prompt)
        self.save_btn = QPushButton("💾 저장")
        self.save_btn.clicked.connect(self.save_prompt)
        self.buttons_layout.addWidget(self.load_btn)
        self.buttons_layout.addWidget(self.save_btn)
        self.layout.addLayout(self.buttons_layout)

        self.setLayout(self.layout)

    def set_role(self, role):
        self.selected_role = role

    def set_type(self, ptype):
        self.selected_type = ptype

    def load_prompt(self):
        if not os.path.exists(self.path):
            self.prompt_input.setText("⚠️ ai_prompts.json 파일이 존재하지 않습니다.")
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            prompts = data.get(self.selected_role, {}).get(self.selected_type, [])
            self.prompt_input.setText("\n".join(prompts))
        except Exception as e:
            self.prompt_input.setText(f"❌ 불러오기 오류: {e}")

    def save_prompt(self):
        text = self.prompt_input.toPlainText().strip()
        if not text:
            self.prompt_input.setText("⚠️ 저장할 프롬프트 내용이 없습니다.")
            return
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}

            if self.selected_role not in data:
                data[self.selected_role] = {}

            data[self.selected_role][self.selected_type] = text.splitlines()

            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.prompt_input.setText("✅ 저장 완료")
        except Exception as e:
            self.prompt_input.setText(f"❌ 저장 실패: {e}")
