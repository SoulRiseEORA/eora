
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from pymongo import MongoClient

class MemorySearchTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["EORA"]
        self.collection = self.db["longterm_memory"]

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("🔍 검색어 입력 (예: AI, 판단, 저장 등)")
        self.search_btn = QPushButton("검색 실행")
        self.search_btn.clicked.connect(self.search_memory)

        self.recheck_btn = QPushButton("장기 기억 재분석 루프 실행")
        self.recheck_btn.clicked.connect(self.run_reanalysis_loop)

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)

        self.layout.addWidget(self.query_input)
        self.layout.addWidget(self.search_btn)
        self.layout.addWidget(self.recheck_btn)
        self.layout.addWidget(self.result_view)
        self.setLayout(self.layout)

    def search_memory(self):
        keyword = self.query_input.text().strip()
        if not keyword:
            return
        results = self.collection.find({"content": {"$regex": keyword, "$options": "i"}})
        display = []
        for i, doc in enumerate(results, 1):
            display.append(f"[{i}] {doc.get('time','?')} :: {doc.get('content','')}")
        self.result_view.setPlainText("\n\n".join(display) if display else "🔍 검색 결과가 없습니다.")

    def run_reanalysis_loop(self):
        from ai_model_selector import do_task
        results = self.collection.find().sort("time", -1).limit(10)
        feedback = []
        for doc in results:
            summary = do_task(
                prompt=f"다음 장기 기억 내용을 다시 평가하여 요약하라. 요약과 활용 가능성도 포함:\n{doc.get('content')}",
                system_message="너는 이오라의 기억 관리자이다. 오래된 장기 기억을 다시 평가해준다.",
                model="gpt-4o"
            )
            feedback.append(f"🧠 {summary}")
        self.result_view.setPlainText("\n---\n".join(feedback) if feedback else "📭 재분석할 내용 없음")
