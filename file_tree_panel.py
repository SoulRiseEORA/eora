from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileSystemModel, QMenu, QPushButton, QHBoxLayout
from PyQt5.QtCore import QDir, Qt
import os

class FileTreePanel(QWidget):
    def __init__(self, root_path=os.getcwd()):
        super().__init__()
        layout = QVBoxLayout(self)

        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_path))
        self.tree.setColumnWidth(0, 300)
        self.tree.doubleClicked.connect(self.open_file)

        # 하단 버튼
        btn_layout = QHBoxLayout()
        self.btn_new_folder = QPushButton("📁 폴더 생성")
        self.btn_new_text = QPushButton("📄 텍스트 생성")
        self.btn_delete = QPushButton("❌ 삭제")
        btn_layout.addWidget(self.btn_new_folder)
        btn_layout.addWidget(self.btn_new_text)
        btn_layout.addWidget(self.btn_delete)

        layout.addWidget(self.tree)
        layout.addLayout(btn_layout)

        # 우클릭 메뉴
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu)

    def open_file(self, index):
        path = self.model.filePath(index)
        print(f"[DEBUG] 더블클릭: {path}")
        # TODO: 코드뷰로 전달 연결

    def context_menu(self, pos):
        index = self.tree.indexAt(pos)
        if not index.isValid():
            return
        menu = QMenu()
        menu.addAction("📁 폴더 생성")
        menu.addAction("📄 텍스트 생성")
        menu.addAction("❌ 삭제")
        menu.exec_(self.tree.viewport().mapToGlobal(pos))
