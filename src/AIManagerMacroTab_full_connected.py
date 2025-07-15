
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QLineEdit, QFileDialog, QListWidget, QMessageBox, QScrollArea, QSizePolicy
)
import tempfile
import os
import traceback
from ai_error_analyzer import AIErrorAnalyzer
from ai_optimizer import AIOptimizer
from builder import ExecutableBuilder
from ai_web_macro_agent import AIWebMacroAgent


class AIManagerMacroTab(QWidget):
    def __init__(self, global_logger=None):
        super().__init__()
        self.logger = global_logger or self.default_logger

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # 첨부 섹션
        self.file_list = QListWidget()
        attach_row = QHBoxLayout()
        self.btn_add_file = QPushButton("📎 기획/설계 파일 추가")
        self.btn_remove_file = QPushButton("❌ 제거")
        attach_row.addWidget(self.btn_add_file)
        attach_row.addWidget(self.btn_remove_file)

        self.btn_add_file.clicked.connect(self.add_files)
        self.btn_remove_file.clicked.connect(self.remove_selected_file)

        # 자동 실행 버튼
        run_row = QHBoxLayout()
        self.btn_run_all = QPushButton("▶ 전체 자동 실행")
        self.btn_stop = QPushButton("⏹ 중지 (미구현)")
        run_row.addWidget(self.btn_run_all)
        run_row.addWidget(self.btn_stop)

        self.btn_run_all.clicked.connect(self.run_all_steps)

        # 로그 출력 (탭 내부용 보조 로그)
        self.local_output = QTextEdit()
        self.local_output.setReadOnly(True)
        self.local_output.setPlaceholderText("📜 자동화 결과 로그 (내부)")

        content_layout.addWidget(QLabel("📁 첨부 파일 목록"))
        content_layout.addWidget(self.file_list)
        content_layout.addLayout(attach_row)
        content_layout.addWidget(QLabel("🔧 자동 실행 제어"))
        content_layout.addLayout(run_row)
        content_layout.addWidget(QLabel("📄 로그 (이 탭 내부 출력용)"))
        content_layout.addWidget(self.local_output)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.analyzer = AIErrorAnalyzer()
        self.optimizer = AIOptimizer()
        self.builder = ExecutableBuilder()
        self.macro = AIWebMacroAgent()

    def log(self, msg):
        self.local_output.append(msg)
        if self.logger:
            self.logger.append(msg)

    def default_logger(self, msg):
        print("[LOG]", msg)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "파일 선택", "", "모든 파일 (*.*)")
        for f in files:
            self.file_list.addItem(f)
            self.log(f"📎 파일 추가됨: {f}")

    def remove_selected_file(self):
        row = self.file_list.currentRow()
        if row >= 0:
            removed = self.file_list.takeItem(row)
            self.log(f"❌ 파일 제거됨: {removed.text()}")

    def run_all_steps(self):
        self.log("▶ 자동화 단계 시작")

        # 1. 파일 분석 (텍스트 기반 파일만)
        for i in range(self.file_list.count()):
            path = self.file_list.item(i).text()
            if not path.endswith((".txt", ".py", ".html")):
                self.log(f"⚠️ 분석 제외 (비지원 확장자): {path}")
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    code = f.read()
                self.log(f"🔍 분석 중: {os.path.basename(path)}")
                result = self.analyzer.analyze_code(code)
                self.log(result)

                optimized = self.optimizer.optimize_code(code)
                self.log("⚙️ 최적화 완료")
            except Exception as e:
                self.log(f"❌ 파일 처리 오류: {e}")

        # 2. 실행파일 빌드
        self.log("🛠 실행파일 빌드 시작")
        result = self.builder.build_executable(source_folder="src")
        self.log(result)

        # 3. 설치 매크로 (예: pyinstaller 자동 설치)
        self.log("🌐 pyinstaller 설치 시도")
        try:
            self.macro.install_tool("pyinstaller")
            self.log("✅ pyinstaller 설치 요청 완료")
        except Exception as e:
            self.log(f"❌ 설치 매크로 오류: {traceback.format_exc()}")

        self.log("🎉 전체 자동화 완료")
