from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("이곳은 로그 분석 패널입니다."))
        self.setLayout(layout)
