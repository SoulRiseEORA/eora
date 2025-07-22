from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel, QMessageBox
from pymongo import MongoClient
from datetime import datetime
import os, json

class PromptPlannerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = MongoClient("mongodb://localhost:27017")['EORA']
        self.training_collection = self.db["training_prompts"]

        self.layout = QVBoxLayout()

        self.suggestion_display = QTextEdit()
        self.suggestion_display.setReadOnly(True)
        self.suggestion_display.setPlaceholderText("💡 이오라 추천 프롬프트 표시 영역")

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("✍️ 작성할 프롬프트 입력")

        self.model_select = QComboBox()
        self.model_select.addItems(["ai1 (이오라)", "ai2 (레조나)", "ai3 (금강)", "ai4", "ai5"])

        self.type_select = QComboBox()
        self.type_select.addItems(["system", "guide", "role", "format", "debug"])

        self.refresh_btn = QPushButton("🔁 이오라 제안 새로고침")
        self.refresh_btn.clicked.connect(self.suggest_prompt_from_aura)

        self.apply_btn = QPushButton("💾 저장")
        self.apply_btn.clicked.connect(self.save_prompt)

        self.recommend_box = QTextEdit()
        self.recommend_box.setPlaceholderText("📚 훈련 프롬프트 목록 (저장 시 DB로 이동)")
        self.load_prompts()

        self.save_train_button = QPushButton("✅ 훈련 프롬프트 저장")
        self.save_train_button.clicked.connect(self.save_to_db)

        self.layout.addWidget(QLabel("💡 이오라 추천 프롬프트"))
        self.layout.addWidget(self.suggestion_display)
        self.layout.addWidget(self.refresh_btn)
        self.layout.addWidget(QLabel("✍️ 직접 작성하기"))
        self.layout.addWidget(self.prompt_input)
        self.layout.addWidget(QLabel("🧠 대상 AI / 유형"))
        self.layout.addWidget(self.model_select)
        self.layout.addWidget(self.type_select)
        self.layout.addWidget(self.apply_btn)
        self.layout.addWidget(QLabel("📚 훈련 프롬프트 기획"))
        self.layout.addWidget(self.recommend_box)
        self.layout.addWidget(self.save_train_button)

        self.setLayout(self.layout)

    def suggest_prompt_from_aura(self):
        cursor = self.db['prompt_history'].find().sort("timestamp", -1).limit(10)
        for doc in cursor:
            if doc.get("importance", 0) >= 80:
                self.suggestion_display.setPlainText(doc.get("content", ""))
                break

    def save_prompt(self):
        model = self.model_select.currentText().split("(")[0].strip()
        section = self.type_select.currentText()
        content = self.prompt_input.toPlainText().strip()
        if not content:
            self.suggestion_display.setPlainText("⚠️ 프롬프트가 비어있습니다.")
            return

        path = "ai_brain/ai_prompts.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
        if model not in data:
            data[model] = {}
        if section not in data[model]:
            data[model][section] = []
        data[model][section].append(content)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.suggestion_display.setPlainText("✅ 저장 완료")
        self.prompt_input.clear()

    def load_prompts(self):
        path = os.path.join("ai_brain", "training_prompts.json")
        if not os.path.exists(path):
            self.recommend_box.setPlainText("⚠️ 훈련 프롬프트가 없습니다.")
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        texts = []
        for item in data.get("prompts", []):
            if isinstance(item, dict):
                texts.append(item.get("text", ""))
            elif isinstance(item, str):
                texts.append(item)
        self.recommend_box.setPlainText("\n\n".join(texts))

    def save_to_db(self):
        text = self.recommend_box.toPlainText().strip()
        prompts = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not prompts:
            QMessageBox.warning(self, "경고", "저장할 프롬프트가 없습니다.")
            return
        for p in prompts:
            self.training_collection.insert_one({
                "prompt": p,
                "source": "이오라추천기획",
                "created_at": datetime.utcnow()
            })
        QMessageBox.information(self, "저장 완료", f"{len(prompts)}개 프롬프트가 훈련 DB에 저장되었습니다.")

# 외부에서 직접 호출 가능한 함수
def insert_training_prompt(prompt: str):
    path = os.path.join("ai_brain", "training_prompts.json")
    os.makedirs("ai_brain", exist_ok=True)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {"prompts": []}
    else:
        data = {"prompts": []}

    if isinstance(data.get("prompts"), list):
        if not any(prompt == item.get("text", "") if isinstance(item, dict) else prompt == item for item in data["prompts"]):
            data["prompts"].append({"text": prompt, "timestamp": datetime.utcnow().isoformat()})
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)