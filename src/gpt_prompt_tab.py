from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout,
    QComboBox, QListWidget, QInputDialog, QMessageBox
)
import json
import os
from gpt_prompt_loader import load_ai_brain_prompt

PROMPT_MEMORY_FILE = "prompt_memory.json"

class GPTPromptTab(QWidget):
    def __init__(self):
        super().__init__()
        self.temperature = 0.5
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.ai_selector = QComboBox()
        self.ai_selector.addItems([
            "AI1_EORA (창의 대화)", "AI2_CODING (정확한 코드)", "AI3_SUMMARY (문서 요약)",
            "AI4_FIXER (코드 수정)", "AI5_UI (UX 표현)", "AI6_MACRO (매크로 설계)"
        ])
        self.ai_selector.currentIndexChanged.connect(self.on_ai_selected)
        layout.addWidget(QLabel("🧠 AI 역할 선택"))
        layout.addWidget(self.ai_selector)

        self.system_input = QTextEdit()
        self.instruction_input = QTextEdit()
        self.role_input = QTextEdit()

        self.system_input.setPlaceholderText("📄 시스템 메시지")
        self.instruction_input.setPlaceholderText("📌 지침 메시지")
        self.role_input.setPlaceholderText("🎯 역할 메시지")

        layout.addWidget(self.system_input)
        layout.addWidget(self.instruction_input)
        layout.addWidget(self.role_input)

        memory_btns = QHBoxLayout()
        self.btn_save = QPushButton("💾 프롬프트 저장")
        self.btn_load = QPushButton("📂 불러오기")
        self.btn_save.clicked.connect(self.save_prompt)
        self.btn_load.clicked.connect(self.load_prompt)
        memory_btns.addWidget(self.btn_save)
        memory_btns.addWidget(self.btn_load)
        layout.addLayout(memory_btns)

        explain_btns = QHBoxLayout()
        self.btn_explain = QPushButton("🧠 자동 설명")
        self.btn_validate = QPushButton("🔍 검수하기")
        self.btn_explain.clicked.connect(self.explain_prompt)
        self.btn_validate.clicked.connect(self.validate_prompt)
        explain_btns.addWidget(self.btn_explain)
        explain_btns.addWidget(self.btn_validate)
        layout.addLayout(explain_btns)

        layout.addWidget(QLabel("✨ 추천 템플릿"))
        self.template_list = QListWidget()
        layout.addWidget(self.setup_template_refresh())
        layout.addWidget(self.template_list)
        self.template_list.itemClicked.connect(self.apply_template)

        layout.addWidget(QLabel("🤖 GPT 응답"))
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.setLayout(layout)
        self.refresh_templates()

    def on_ai_selected(self):
        ai_key = self.ai_selector.currentText().split(" ")[0]
        prompt_data = load_ai_brain_prompt(ai_key)

        self.system_input.setPlainText(prompt_data.get("system", ""))
        self.instruction_input.setPlainText(prompt_data.get("instruction", ""))
        self.role_input.setPlainText(prompt_data.get("role", ""))
        self.temperature = float(prompt_data.get("temperature", 0.5))

        opinion = prompt_data.get("opinion", "").strip()
        if opinion:
            self.template_list.addItem("📩 AI 의견: " + opinion)

    def send_prompt_to_api(self):
        import openai
        system_msg = self.system_input.toPlainText()
        instruction_msg = self.instruction_input.toPlainText()
        role_msg = self.role_input.toPlainText()

        prompt = f"{instruction_msg}\n\n{role_msg}"
        self.result_display.setPlainText("⏳ 응답 대기 중...")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=800
            )
            reply = response.choices[0].message.content.strip()
            self.result_display.setPlainText(reply)
        except Exception as e:
            self.result_display.setPlainText(f"❌ 호출 실패: {e}")

    def save_prompt(self):
        prompt_text = self.role_input.toPlainText()
        try:
            with open("ai_brain/ai_prompts.json", "w", encoding="utf-8") as f:
                json.dump({"user_prompt": prompt_text}, f, ensure_ascii=False, indent=4)
            self.result_display.append("✅ 프롬프트가 성공적으로 저장되었습니다.")
        except Exception as e:
            self.result_display.append(f"❌ 프롬프트 저장 실패: {str(e)}")

    def load_prompt(self):
        memory = self._load_memory()
        if not memory:
            QMessageBox.warning(self, "불러오기 실패", "저장된 프롬프트가 없습니다.")
            return
        name, ok = QInputDialog.getItem(self, "불러오기", "프롬프트 선택:", list(memory.keys()), 0, False)
        if ok and name:
            data = memory[name]
            self.system_input.setPlainText(data.get("system", ""))
            self.instruction_input.setPlainText(data.get("instruction", ""))
            self.role_input.setPlainText(data.get("role", ""))

    def explain_prompt(self):
        text = self.role_input.toPlainText()
        explanation = "📘 이 프롬프트는 GPT에게 다음을 수행하라는 요청입니다:\n→ " + text[:100]
        QMessageBox.information(self, "프롬프트 설명", explanation)

    def validate_prompt(self):
        text = self.role_input.toPlainText().lower()
        if "해줘" in text or "설명" in text or "요약" in text:
            QMessageBox.information(self, "✅ 검수 결과", "문맥상 명확합니다.")
        else:
            QMessageBox.warning(self, "⚠️ 검수 결과", "의도 파악이 어렵습니다. 더 구체적으로 작성해보세요.")

    def apply_template(self, item):
        self.role_input.setPlainText(item.text())

    def _load_memory(self):
        if os.path.exists(PROMPT_MEMORY_FILE):
            with open(PROMPT_MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_templates_from_json(self, json_path="cobot_features.json"):
        if not os.path.exists(json_path):
            return
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                self.template_list.clear()
                for i in items[:50]:
                    msg = f"{i.get('기능명', '')} → {i.get('설명', '')}"
                    self.template_list.addItem(msg)
        except Exception as e:
            print("[ERROR] 프롬프트 템플릿 불러오기 실패:", e)

    def setup_template_refresh(self):
        self.refresh_template_btn = QPushButton("🔄 템플릿 새로고침")
        self.refresh_template_btn.clicked.connect(self.refresh_templates)
        return self.refresh_template_btn

    def refresh_templates(self):
        try:
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017/")
            db = client["eora_ai"]
            collection = db["cobot_features"]
            items = list(collection.find().sort("중요도", -1).limit(20))
            self.template_list.clear()
            for i in items:
                msg = f"{i.get('기능명', '')} → {i.get('설명', '')}"
                self.template_list.addItem(msg)
        except Exception as e:
            self.template_list.clear()
            self.template_list.addItem("❗ MongoDB에서 추천 프롬프트 불러오기 실패")
