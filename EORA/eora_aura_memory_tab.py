"""
EORA/eora_aura_memory_tab.py

AURA DB 검색 및 회상 탭
- Redis 캐시 + MongoDB 통합 회상 기능
- recall_memory() 통합 호출부
"""
import asyncio
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel
from EORA.aura_memory_service import recall_memory

class AURAMemoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.label = QLabel("🧠 AURA 메모리 검색")
        self.input = QLineEdit()
        self.input.setPlaceholderText("검색 키워드 입력")
        self.search_btn = QPushButton("🔍 검색")
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.search_btn)
        self.layout.addWidget(self.result_view)
        self.setLayout(self.layout)

        self.search_btn.clicked.connect(self.on_search)

    def on_search(self):
        kw = self.input.text().strip()
        if not kw:
            return
        self.result_view.append(f"🔄 '{kw}' 회상 중...")
        asyncio.create_task(self.do_search(kw))

    async def do_search(self, kw):
        try:
            docs = await recall_memory(kw)
            if not docs:
                self.result_view.append("❌ 결과 없음")
                return
            self.result_view.append(f"✅ {len(docs)}개 문서 회상됨:")
            for doc in docs:
                summary = doc.get("summary_prompt") or (doc.get("content") or "")[:50]
                t = doc.get("type", doc.get("origin", "unknown"))
                self.result_view.append(f"- [{t}] {summary}")
        except Exception as e:
            self.result_view.append(f"❌ 오류: {e}")
