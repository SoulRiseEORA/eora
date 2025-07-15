from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QListWidget, QSplitter
)
import os
from EORA.eora_simulation_file_loader import SimulationFileLoader

class EORAUnifiedRecordTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📖 학습 기록 및 시뮬레이션"))

        splitter = QSplitter()
        splitter.setOrientation(1)  # 수직

        self.record_list = QListWidget()
        self.record_list.addItem("🧠 최근 훈련 기록")
        self.record_list.addItems(self.load_recent_train_logs())
        splitter.addWidget(self.record_list)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        splitter.addWidget(self.log_view)

        layout.addWidget(splitter)

        layout.addWidget(SimulationFileLoader())  # 파일 분석기 UI 삽입

        self.record_list.currentTextChanged.connect(self.show_record_content)

    def load_recent_train_logs(self):
        folder = "chat_logs"
        logs = []
        if os.path.exists(folder):
            for file in sorted(os.listdir(folder), reverse=True):
                if file.endswith(".json"):
                    logs.append(file)
        return logs

    def show_record_content(self, filename):
        if filename.endswith(".json"):
            try:
                path = os.path.join("chat_logs", filename)
                with open(path, "r", encoding="utf-8") as f:
                    import json
                    data = json.load(f)
                    self.log_view.clear()
                    for item in data:
                        user = item.get("user", "")
                        reply = item.get("reply", "")
                        self.log_view.append(f"👤 {user}")
                        self.log_view.append(f"🤖 {reply}")
                        self.log_view.append("—" * 20)
            except Exception as e:
                self.log_view.setText(f"❌ 읽기 실패: {e}")