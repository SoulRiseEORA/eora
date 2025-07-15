from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class OptimizerPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("코드 최적화 패널입니다."))
        self.setLayout(layout)
