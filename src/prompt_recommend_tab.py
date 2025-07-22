
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
import json, os

RECOMMEND_FILE = "ai_prompt_recommended.json"

class PromptRecommendTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel("⭐ AI별 추천 프롬프트 (최근 높은 점수 순)")
        self.listbox = QListWidget()
        layout.addWidget(self.label)
        layout.addWidget(self.listbox)
        self.refresh()

    def refresh(self):
        self.listbox.clear()
        if not os.path.exists(RECOMMEND_FILE):
            self.listbox.addItem("⚠️ 추천 데이터가 없습니다.")
            return
        with open(RECOMMEND_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for ai, prompts in data.items():
            self.listbox.addItem(f"[{ai}] 추천 TOP 5")
            for p in prompts[:5]:
                self.listbox.addItem(" • " + p)
