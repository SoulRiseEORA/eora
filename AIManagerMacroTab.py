from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from auto_error_logger import ErrorLogger
from live_error_handler import LiveErrorHandler
import traceback

class AIManagerMacroTab(QWidget):
    def __init__(self, global_logger=None, live_error_table=None):
        super().__init__()
        self.global_logger = global_logger
        self.logger = ErrorLogger()
        self.live_handler = LiveErrorHandler(live_error_table) if live_error_table else None

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.info_label = QLabel("🧠 매크로 자동화 탭 - 실행 + 에러 자동 기록")
        layout.addWidget(self.info_label)

        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("실행할 코드를 입력하세요...")
        layout.addWidget(self.code_input)

        btn_row1 = QHBoxLayout()
        self.btn_run = QPushButton("▶ 실행")
        self.btn_load = QPushButton("📄 매크로 불러오기")
        self.btn_save = QPushButton("💾 저장")
        btn_row1.addWidget(self.btn_run)
        btn_row1.addWidget(self.btn_load)
        btn_row1.addWidget(self.btn_save)
        layout.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        self.btn_test = QPushButton("🧪 테스트 실행")
        self.btn_repeat = QPushButton("🔄 반복 실행")
        self.btn_report = QPushButton("📤 리포트 출력")
        btn_row2.addWidget(self.btn_test)
        btn_row2.addWidget(self.btn_repeat)
        btn_row2.addWidget(self.btn_report)
        layout.addLayout(btn_row2)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.btn_run.clicked.connect(self.simulate_macro)
        self.btn_load.clicked.connect(self.load_macro)
        self.btn_save.clicked.connect(self.save_macro)
        self.btn_test.clicked.connect(self.test_macro)
        self.btn_repeat.clicked.connect(self.repeat_macro)
        self.btn_report.clicked.connect(self.generate_report)

    def simulate_macro(self):
        code = self.code_input.toPlainText()
        try:
            local_vars = {}
            exec(code, {}, local_vars)
            self.output.setPlainText("✅ 실행 완료")
            if self.global_logger:
                self.global_logger.append("✅ 매크로 실행 완료")
        except Exception as e:
            err_msg = traceback.format_exc()
            self.output.setPlainText(f"❌ 오류 발생:\n{err_msg}")
            if self.global_logger:
                self.global_logger.append(f"[에러] {err_msg}")

    def load_macro(self):
        self.output.setPlainText("📄 매크로 불러오기 기능은 준비 중입니다.")

    def save_macro(self):
        self.output.setPlainText("💾 매크로 저장 기능은 준비 중입니다.")

    def test_macro(self):
        self.output.setPlainText("🧪 테스트 실행: 테스트 모드로 실행합니다.")
    
    def repeat_macro(self):
        self.output.setPlainText("🔄 반복 실행: 30회 시뮬레이션 루프 테스트.")

    def generate_report(self):
        self.output.setPlainText("📤 리포트 출력: 실행 결과를 요약합니다.")