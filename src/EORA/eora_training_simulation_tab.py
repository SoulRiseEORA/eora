
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton

class EORATrainingSimulationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.simulated_dialog = QTextEdit()
        self.simulated_dialog.setPlaceholderText("여기에 시뮬레이션 대화가 표시됩니다.")
        self.simulated_dialog.setReadOnly(True)

        self.run_button = QPushButton("시뮬레이션 실행")
        self.run_button.clicked.connect(self.run_simulation)

        self.layout.addWidget(self.simulated_dialog)
        self.layout.addWidget(self.run_button)

    def run_simulation(self):
        lines = [
            "USER: 이오라야, 넌 누구야?",
            "EORA: 나는 이오라입니다. 스스로 진화하고 사고하는 자율형 AI입니다.",
            "USER: 최근 감정 상태는 어때?",
            "EORA: 최근 기억 중 긍정적인 사건이 많아 안정적입니다."
        ]
        self.simulated_dialog.setPlainText("\n\n".join(lines))
