
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QPushButton,
    QHBoxLayout, QTableWidgetItem, QHeaderView, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import datetime

# ✅ AIManagerTab 탭용: 에러노트 (MongoDB 누적 기록)
class EnhancedErrorNotebook(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📘 에러노트 (MongoDB 누적 기록)"))

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["선택", "에러 메시지", "파일명", "탭 위치", "발생일", "회차"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        row_buttons = QHBoxLayout()
        self.select_all = QCheckBox("전체 선택")
        self.btn_reload = QPushButton("🔄 새로고침")
        self.btn_delete = QPushButton("🗑 삭제")
        row_buttons.addWidget(self.select_all)
        row_buttons.addWidget(self.btn_reload)
        row_buttons.addWidget(self.btn_delete)
        layout.addLayout(row_buttons)

        self.setLayout(layout)

        self.select_all.stateChanged.connect(self.toggle_all)
        self.btn_reload.clicked.connect(self.load_from_mongo)
        self.btn_delete.clicked.connect(self.delete_selected)

        self.mongo = MongoClient("mongodb://localhost:27017/")["EORA"]["error_notes"]
        self.load_from_mongo()

    def toggle_all(self, state):
        for row in range(self.table.rowCount()):
            cb = self.table.cellWidget(row, 0)
            cb.setChecked(state == Qt.Checked)

    def load_from_mongo(self):
        self.table.setRowCount(0)
        for doc in self.mongo.find().sort("timestamp", -1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            cb = QCheckBox()
            self.table.setCellWidget(row, 0, cb)
            self.table.setItem(row, 1, QTableWidgetItem(doc.get("error", "")))
            self.table.setItem(row, 2, QTableWidgetItem(doc.get("file", "")))
            self.table.setItem(row, 3, QTableWidgetItem(doc.get("tab", "")))
            self.table.setItem(row, 4, QTableWidgetItem(doc.get("timestamp", "").strftime("%Y-%m-%d %H:%M") if "timestamp" in doc else ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(doc.get("repeat", 1))))

    def delete_selected(self):
        for row in reversed(range(self.table.rowCount())):
            if self.table.cellWidget(row, 0).isChecked():
                err = self.table.item(row, 1).text()
                self.mongo.delete_many({"error": err})
                self.table.removeRow(row)

# ✅ 에러관리 탭용: 실시간 에러 대응 현황
class ErrorNotebook(QWidget):  # 이름 변경 없이 기존 연결 유지
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📡 실시간 에러 현황"))

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["에러 메시지", "파일명", "탭 위치", "발생 시각"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.add_live_error("SyntaxError: unexpected EOF", "GPTMainWindow.py", "GPT 대화")
        self.add_live_error("ZeroDivisionError: division by zero", "ai_math.py", "수식 계산기")

    def add_live_error(self, msg, file, tab):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(msg))
        self.table.setItem(row, 1, QTableWidgetItem(file))
        self.table.setItem(row, 2, QTableWidgetItem(tab))
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.table.setItem(row, 3, QTableWidgetItem(now))

# ✅ 테스트 파일 관리
class TestFileTrackerPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🧪 테스트 파일 목록"))

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["선택", "파일명", "경로", "생성일", "코드 요약"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        self.select_all = QCheckBox("전체 선택")
        self.btn_delete = QPushButton("🗑 삭제")
        self.btn_download = QPushButton("⬇ 다운로드")
        controls.addWidget(self.select_all)
        controls.addWidget(self.btn_delete)
        controls.addWidget(self.btn_download)
        layout.addLayout(controls)

        self.select_all.stateChanged.connect(self.toggle_all)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_download.clicked.connect(self.download_selected)

        self.setLayout(layout)
        self.insert_dummy_data()

    def insert_dummy_data(self):
        data = [
            ("test_001.py", "C:/tests", "2025-04-12", "// 임시 테스트 코드 1"),
            ("debug_ai2.py", "C:/tests", "2025-04-13", "// 디버그용 테스트 코드")
        ]
        for row_data in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            cb = QCheckBox()
            self.table.setCellWidget(row, 0, cb)
            for i, v in enumerate(row_data):
                self.table.setItem(row, i+1, QTableWidgetItem(v))

    def toggle_all(self, state):
        for r in range(self.table.rowCount()):
            cb = self.table.cellWidget(r, 0)
            cb.setChecked(state == Qt.Checked)

    def delete_selected(self):
        for r in reversed(range(self.table.rowCount())):
            if self.table.cellWidget(r, 0).isChecked():
                self.table.removeRow(r)

    def download_selected(self):
        for r in range(self.table.rowCount()):
            if self.table.cellWidget(r, 0).isChecked():
                fname = self.table.item(r, 1).text()
                QFileDialog.getSaveFileName(self, "파일 저장", fname)

# ✅ 롤백 파일 관리
class RollbackManagerPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("⏪ 롤백 백업 파일 목록"))

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["선택", "버전명", "경로", "생성일", "코드 요약"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        self.select_all = QCheckBox("전체 선택")
        self.btn_delete = QPushButton("🗑 삭제")
        self.btn_download = QPushButton("⬇ 다운로드")
        controls.addWidget(self.select_all)
        controls.addWidget(self.btn_delete)
        controls.addWidget(self.btn_download)
        layout.addLayout(controls)

        self.select_all.stateChanged.connect(self.toggle_all)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_download.clicked.connect(self.download_selected)

        self.setLayout(layout)
        self.insert_dummy_data()

    def insert_dummy_data(self):
        data = [
            ("backup_v1.py", "C:/rollback", "2025-04-10", "# 안정화된 버전 1"),
            ("backup_v2.py", "C:/rollback", "2025-04-13", "# 디버깅 전 백업본")
        ]
        for row_data in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            cb = QCheckBox()
            self.table.setCellWidget(row, 0, cb)
            for i, v in enumerate(row_data):
                self.table.setItem(row, i+1, QTableWidgetItem(v))

    def toggle_all(self, state):
        for r in range(self.table.rowCount()):
            cb = self.table.cellWidget(r, 0)
            cb.setChecked(state == Qt.Checked)

    def delete_selected(self):
        for r in reversed(range(self.table.rowCount())):
            if self.table.cellWidget(r, 0).isChecked():
                self.table.removeRow(r)

    def download_selected(self):
        for r in range(self.table.rowCount()):
            if self.table.cellWidget(r, 0).isChecked():
                fname = self.table.item(r, 1).text()
                QFileDialog.getSaveFileName(self, "파일 저장", fname)
