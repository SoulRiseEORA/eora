
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QListWidget, QInputDialog, QMessageBox, QFileDialog, QSplitter, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt
import os

PROJECT_HTML_DIR = "project_docs"
os.makedirs(PROJECT_HTML_DIR, exist_ok=True)

class ProjectPlanningPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        self.splitter = QSplitter(Qt.Horizontal)

        # 왼쪽: 프로젝트 리스트 (트리창 역할)
        self.project_list = QListWidget()
        self.project_list.setMinimumWidth(220)
        self.project_list.addItem("금강GPT")
        self.project_list.addItem("코봇개발기획")

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("➕ 추가")
        self.btn_del = QPushButton("🗑 삭제")
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_del)

        self.btn_add.clicked.connect(self.add_project)
        self.btn_del.clicked.connect(self.delete_project)
        self.project_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_list.customContextMenuRequested.connect(self.project_context_menu)

        left = QVBoxLayout()
        left.addWidget(QLabel("📁 기획 프로젝트 목록"))
        left.addWidget(self.project_list)
        left.addLayout(btn_row)

        left_widget = QWidget()
        left_widget.setLayout(left)

        # 중앙: HTML 기반 기획서 편집기
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("📝 여기에 프로그램 기획서를 입력하거나 수정하세요...")
        self.editor.setAcceptRichText(True)

        code_btns = QHBoxLayout()
        self.btn_undo = QPushButton("↩ 되돌리기")
        self.btn_copy = QPushButton("📋 복사")
        self.btn_save = QPushButton("💾 HTML 저장")
        self.btn_undo.clicked.connect(self.editor.undo)
        self.btn_copy.clicked.connect(self.editor.copy)
        self.btn_save.clicked.connect(self.save_html)

        code_btns.addWidget(self.btn_undo)
        code_btns.addWidget(self.btn_copy)
        code_btns.addWidget(self.btn_save)

        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.editor_context_menu)

        mid = QVBoxLayout()
        mid.addWidget(QLabel("🧾 프로그램 기획서 (HTML 미리보기/편집)"))
        mid.addWidget(self.editor)
        mid.addLayout(code_btns)

        mid_widget = QWidget()
        mid_widget.setLayout(mid)

        # 오른쪽: AI 대화 로그 + 입력창
        self.chat_log = QTextEdit()
        self.chat_log.setPlaceholderText("🤖 AI1 금강 + 보조 AI들과의 대화 기록")
        self.chat_log.setReadOnly(True)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("💬 AI에게 의견 남기기...")

        right = QVBoxLayout()
        right.addWidget(QLabel("🤖 프로젝트 관련 대화창"))
        right.addWidget(self.chat_log)
        right.addWidget(self.chat_input)

        right_widget = QWidget()
        right_widget.setLayout(right)

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(mid_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([200, 700, 400])

        layout.addWidget(self.splitter)

    def add_project(self):
        name, ok = QInputDialog.getText(self, "프로젝트 추가", "프로젝트 이름:")
        if ok and name:
            self.project_list.addItem(name)

    def delete_project(self):
        row = self.project_list.currentRow()
        if row >= 0:
            name = self.project_list.item(row).text()
            confirm = QMessageBox.question(self, "삭제 확인", f"{name}을 삭제할까요?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.project_list.takeItem(row)
                html_path = os.path.join(PROJECT_HTML_DIR, f"{name}.html")
                chat_path = os.path.join(PROJECT_HTML_DIR, f"{name}_chat.txt")
                if os.path.exists(html_path):
                    os.remove(html_path)
                if os.path.exists(chat_path):
                    os.remove(chat_path)

    def save_html(self):
        name = self.project_list.currentItem().text() if self.project_list.currentItem() else "기획서"
        html_path = os.path.join(PROJECT_HTML_DIR, f"{name}.html")
        content = self.editor.toHtml()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        QMessageBox.information(self, "저장 완료", f"{html_path}에 저장되었습니다.")

    def editor_context_menu(self, pos):
        menu = self.editor.createStandardContextMenu()
        menu.exec_(self.editor.viewport().mapToGlobal(pos))

    def project_context_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("이름 변경", self.rename_project)
        menu.addAction("삭제", self.delete_project)
        menu.exec_(self.project_list.viewport().mapToGlobal(pos))

    def rename_project(self):
        row = self.project_list.currentRow()
        if row >= 0:
            name = self.project_list.item(row).text()
            new_name, ok = QInputDialog.getText(self, "이름 변경", "새 이름:", text=name)
            if ok and new_name:
                self.project_list.item(row).setText(new_name)
