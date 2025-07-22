from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QFileDialog, QProgressBar
from PyQt5.QtCore import Qt, pyqtSignal
from error_notebook import ErrorNotebook
from chat_input_area import ChatInputArea
from file_processor import FileProcessor
from ai_chat import get_eora_instance
import os
import asyncio
import json

class GPTChatPanel(QWidget):
    # 사용자 입력 처리를 위한 시그널 정의
    send_user_input = pyqtSignal(str)

    def __init__(self, session_name="기본 세션", fresh=False):
        super().__init__()
        self.eora = get_eora_instance()
        self.processor = FileProcessor()
        self.error_notebook = ErrorNotebook()
        self.current_session = session_name
        self.fresh = fresh
        self.attached_file = None

        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setStyleSheet("font-size:14px; padding:10px;")

        self.input_area = ChatInputArea()
        self.input_area.setFixedHeight(80)

        self.send_button = QPushButton("전송")
        self.attach_button = QPushButton("📁")
        self.clear_button = QPushButton("지우기")

        button_column = QVBoxLayout()
        button_column.setSpacing(5)
        button_column.addWidget(self.attach_button)
        button_column.addWidget(self.send_button)
        button_column.addWidget(self.clear_button)
        button_column.addStretch()

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        input_row.addWidget(self.input_area, 8)
        input_row.addLayout(button_column, 1)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setMaximum(100)
        self.progress.setTextVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addLayout(input_row)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.send_button.clicked.connect(self.manual_send)
        self.attach_button.clicked.connect(self.select_file)
        self.clear_button.clicked.connect(lambda: self.chat_display.clear())
        self.input_area.send_message.connect(self.manual_send)

        self.load_session(self.current_session)

    def append_message_to_display(self, role: str, content: str):
        """채팅창에 메시지를 표시합니다."""
        # HTML 형식으로 역할과 내용을 꾸며서 추가
        formatted_content = content.replace('\\n', '<br>')
        if role.lower() == 'user':
            html = f'<div style="text-align: right; margin: 5px;"><b>👤 {role}</b><br>{formatted_content}</div>'
        else:
            html = f'<div style="text-align: left; margin: 5px;"><b>🧠 {role}</b><br>{formatted_content}</div>'
        self.chat_display.append(html)

    def select_file(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "첨부 파일 선택")
            if path and os.path.exists(path):
                self.attached_file = path
                self.input_area.setPlainText(f"{self.input_area.toPlainText()} [첨부됨: {os.path.basename(path)}]")
        except Exception as e:
            self.chat_display.append(f"❌ 첨부 실패: {str(e)}")

    def manual_send(self):
        text = self.input_area.toPlainText().strip()
        if text:
            self.input_area.clear()
            self.input_area.setFocus()
            
            # 사용자 입력을 UI에 먼저 표시
            self.append_message_to_display("User", text)
            
            # 회상 트리거 감지 및 perform_recall 호출
            if any(trigger in text for trigger in ["/회상", "기억", "전에"]):
                try:
                    from ai_chat_recall import perform_recall
                    recall_context = perform_recall({"query": text})
                    if recall_context:
                        self.append_message_to_display("system", "[회상 결과]\n" + "\n".join(str(x) for x in recall_context))
                except Exception as e:
                    self.append_message_to_display("system", f"회상 호출 오류: {e}")
            
            # 처리 로직을 메인 윈도우로 전달
            self.send_user_input.emit(text)

    def load_session(self, name):
        self.current_session = name
        try:
            path = f"chat_logs/{name}/chat.txt"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.chat_display.setText(f.read())
                    self.chat_display.append(f"<span style='color:gray;'>📂 세션 '{name}' 불러오기 완료</span>")
            else:
                self.chat_display.setText("")
                self.chat_display.append(f"<span style='color:gray;'>ℹ️ '{name}/chat.txt' 파일이 없습니다</span>")
        except Exception as e:
            self.chat_display.setText("")
            self.chat_display.append(f"<span style='color:red;'>❌ 불러오기 실패: {e}</span>")

    def set_session(self, session_name: str):
        """세션 이름을 변경하고, 필요시 대화 기록을 불러옵니다."""
        self.current_session = session_name
        self.load_session(session_name)
