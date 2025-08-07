from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class UIDesignPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("여기는 UI/UX 설계 탭입니다."))
        self.setLayout(layout)
