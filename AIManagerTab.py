from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox
)
import os, json, random

AI_PROMPT_PATH = os.path.join("ai_brain", "ai_prompts.json")
REF_PATH = "prompt_db_reference_1000.json"

class AIManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(800)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🤖 AI 프롬프트 선택 및 편집"))

        top = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems([f"ai{i}" for i in range(2, 7)])
        self.combo.currentTextChanged.connect(self.load_selected_ai)
        top.addWidget(QLabel("AI 선택"))
        top.addWidget(self.combo)
        layout.addLayout(top)

        self.fields = {}
        for label in ["system", "role", "guide", "format"]:
            layout.addWidget(QLabel(f"[{label}]"))
            edit = QTextEdit()
            edit.setMinimumHeight(80)
            self.fields[label] = edit
            layout.addWidget(edit)

        self.save_btn = QPushButton("💾 선택한 AI 저장")
        self.save_btn.clicked.connect(self.save_ai_prompt)
        layout.addWidget(self.save_btn)

        layout.addWidget(QLabel("🎲 프롬프트 추천 보기 (20개 랜덤)"))
        self.recommend = QTextEdit()
        self.recommend.setReadOnly(True)
        layout.addWidget(self.recommend)

        self.refresh_btn = QPushButton("🔁 새로고침")
        self.refresh_btn.clicked.connect(self.load_random)
        layout.addWidget(self.refresh_btn)

        self.data = {}
        self.load_all()
        self.load_selected_ai("ai2")

    def load_all(self):
        try:
            if os.path.exists(AI_PROMPT_PATH):
                with open(AI_PROMPT_PATH, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            else:
                self.data = {f"ai{i}": {} for i in range(1, 7)}
        except:
            self.data = {}

    def load_selected_ai(self, ai_key):
        block = self.data.get(ai_key, {})
        for k in self.fields:
            value = block.get(k, "")
            if isinstance(value, list):
                value = "\n\n".join(value)
            self.fields[k].setText(value)

    def clean_prompt_list(self, prompt_list):
        # 1. 각 항목 strip, 2. 빈 항목 제거, 3. 중복 제거(순서 유지)
        seen = set()
        result = []
        for item in prompt_list:
            s = item.strip()
            if s and s not in seen:
                seen.add(s)
                result.append(s)
        return result

    def save_ai_prompt(self):
        ai_key = self.combo.currentText()
        if ai_key not in self.data:
            self.data[ai_key] = {}
        for k in self.fields:
            value = self.fields[k].toPlainText().strip()
            prompt_list = [v for v in value.split("\n\n") if v.strip()]
            prompt_list = self.clean_prompt_list(prompt_list)
            self.data[ai_key][k] = prompt_list
        try:
            # 저장 JSON
            with open(AI_PROMPT_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            # 저장 TXT
            txt = "\n\n".join([f"[{k}]\n" + "\n\n".join(self.data[ai_key][k]) for k in self.fields])
            txt_path = os.path.join("ai_brain", f"{ai_key.upper()}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(txt)
            self.recommend.setPlainText("✅ 저장 완료 (자동 정제 + JSON + TXT)")
        except Exception as e:
            self.recommend.setPlainText(f"❌ 저장 실패: {e}")

    def load_random(self):
        if not os.path.exists(REF_PATH):
            self.recommend.setPlainText("⚠️ prompt_db_reference_1000.json 없음")
            return
        try:
            with open(REF_PATH, "r", encoding="utf-8") as f:
                data = list(json.load(f).values())
            random.shuffle(data)
            self.recommend.setPlainText("\n".join(data[:20]))
        except Exception as e:
            self.recommend.setPlainText(f"❌ 추천 실패: {e}")