from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class CodeGenPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("코드 생성기 패널입니다."))
        self.setLayout(layout)
