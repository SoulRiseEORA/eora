
from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout

class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.log_area)
        self.setLayout(layout)

    def log(self, message: str):
        self.log_area.append(message)
