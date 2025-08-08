
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton,
    QHBoxLayout, QMenu, QInputDialog
)
from PyQt5.QtCore import pyqtSignal, Qt
import os

class SessionPanel(QWidget):
    session_selected = pyqtSignal(str)

    def __init__(self, session_dir="session_data"):
        super().__init__()
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.emit_selected_session)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        self.add_btn = QPushButton("세션 추가")
        self.del_btn = QPushButton("세션 삭제")

        self.add_btn.clicked.connect(self.add_session)
        self.del_btn.clicked.connect(self.delete_session)

        btns = QHBoxLayout()
        btns.addWidget(self.add_btn)
        btns.addWidget(self.del_btn)

        layout.addWidget(self.list_widget)
        layout.addLayout(btns)

        self.refresh_sessions()

    def emit_selected_session(self, item):
        self.session_selected.emit(item.text())

    def refresh_sessions(self):
        self.list_widget.clear()
        for name in sorted(os.listdir(self.session_dir)):
            self.list_widget.addItem(name)

    def add_session(self):
        count = len(os.listdir(self.session_dir)) + 1
        name = f"세션{count}"
        os.makedirs(os.path.join(self.session_dir, name), exist_ok=True)
        self.refresh_sessions()

    def delete_session(self):
        item = self.list_widget.currentItem()
        if item:
            path = os.path.join(self.session_dir, item.text())
            if os.path.exists(path):
                import shutil
                shutil.rmtree(path)
            self.refresh_sessions()

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item:
            menu = QMenu()
            rename_action = menu.addAction("이름 변경")
            delete_action = menu.addAction("삭제")
            action = menu.exec_(self.list_widget.mapToGlobal(pos))
            if action == rename_action:
                new_name, ok = QInputDialog.getText(self, "이름 변경", "새 이름 입력", text=item.text())
                if ok and new_name:
                    old_path = os.path.join(self.session_dir, item.text())
                    new_path = os.path.join(self.session_dir, new_name)
                    os.rename(old_path, new_path)
                    self.refresh_sessions()
            elif action == delete_action:
                self.delete_session()
