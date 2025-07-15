"""
GPT 채팅 패널
- 채팅 UI
- 메시지 처리
"""

import os
import logging
import asyncio
from typing import Dict, Any
from concurrent.futures import CancelledError
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QFont, QIcon, QKeyEvent
from datetime import datetime

# chat_session_manager와 ai_chat 모듈 임포트
from chat_session_manager import append_message, load_messages, delete_chat_log
from aura_system.ai_chat import get_eora_ai
from aura_system.memory_manager import MemoryManagerAsync, get_memory_manager_sync
from aura_system.task_manager import add_task

# logger = logging.getLogger(__name__)

class ChatWorker(QThread):
    """백그라운드에서 AI 응답을 처리하는 워커 스레드"""
    response_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, user_input: str, main_loop, trigger_context: dict, eai_system: Any = None, parent=None):
        super().__init__(parent)
        self.user_input = user_input
        self.main_loop = main_loop
        self.trigger_context = trigger_context
        self.eai_system = eai_system
        self.memory_manager = get_memory_manager_sync()

    def run(self):
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.get_response_async(), self.main_loop
            )
            response = future.result()
            self.response_ready.emit(response)
        except CancelledError:
            # 애플리케이션 종료 시 정상적으로 발생할 수 있는 오류이므로 정보 수준으로 로깅
            # logger.info("ChatWorker 작업이 취소되었습니다 (일반적으로 종료 시 발생).")
            pass
        except Exception as e:
            # logger.error(f"ChatWorker 실행 오류: {e}", exc_info=True)
            self.error_occurred.emit(str(e))

    async def get_response_async(self):
        eora_ai = await get_eora_ai(self.memory_manager)
        return await eora_ai.respond_async(
            self.user_input, 
            trigger_context=self.trigger_context,
            eai_system=self.eai_system
        )


class CustomTextEdit(QTextEdit):
    """Enter 키 전송, Shift+Enter 줄바꿈을 위한 커스텀 QTextEdit"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            if hasattr(self.parent_widget, 'send_message'):
                self.parent_widget.send_message()
            event.accept()
        else:
            super().keyPressEvent(event)


class GPTChatPanel(QWidget):
    """GPT 채팅 패널 UI 및 로직"""
    # 백그라운드에서 생성된 asyncio Task 리스트를 전달하기 위한 시그널
    tasks_created = pyqtSignal(list)

    def __init__(self, session_name: str, eai_system: Any = None, parent=None):
        super().__init__(parent)
        self.session_name = session_name
        self.eai_system = eai_system
        self.memory_manager = get_memory_manager_sync()
        self.last_user_input = "" # 마지막 사용자 입력을 저장할 변수
        self.setup_ui()
        self.load_chat_history(session_name)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("맑은 고딕", 10))
        layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_field = CustomTextEdit(self)
        self.input_field.setFont(QFont("맑은 고딕", 10))
        self.input_field.setPlaceholderText("메시지를 입력하세요... (Enter로 전송, Shift+Enter로 줄바꿈)")
        self.input_field.setFixedHeight(80)
        input_layout.addWidget(self.input_field)

        button_layout = QVBoxLayout()
        
        # 전송 버튼
        self.send_button = QPushButton("전송")
        self.send_button.setIcon(QIcon("icons/send.png")) # 아이콘 경로 확인 필요
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        # 파일 버튼
        self.file_button = QPushButton("파일")
        self.file_button.setIcon(QIcon("icons/file.png")) # 아이콘 경로 확인 필요
        self.file_button.clicked.connect(self.load_file)
        button_layout.addWidget(self.file_button)

        # 지우기 버튼
        self.clear_button = QPushButton("지우기")
        self.clear_button.setIcon(QIcon("icons/clear.png")) # 아이콘 경로 확인 필요
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)
        
        input_layout.addLayout(button_layout)
        layout.addLayout(input_layout)

    def send_message(self):
        user_input = self.input_field.toPlainText().strip()
        if not user_input:
            return
        
        self.last_user_input = user_input # 사용자 입력 저장

        self.display_message("User", user_input)
        self.input_field.clear()

        # 트리거 탐지는 이제 ai_chat.py에서 전담하므로, 빈 컨텍스트를 전달합니다.
        trigger_context = {}
        
        # ChatWorker를 통해 AI 응답 비동기 처리
        main_loop = asyncio.get_event_loop()
        self.worker = ChatWorker(user_input, main_loop, trigger_context, self.eai_system, self)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, response: Dict[str, Any]):
        role = response.get("role", "AI")
        ai_response = response.get("response", "응답이 없습니다.")
        
        # ai_chat에서 반환된 Task 리스트를 가져옴
        tasks = response.get("tasks", [])
        if tasks:
            # 시그널을 통해 MainWindow로 Task 리스트 전달
            self.tasks_created.emit(tasks)
            
        self.display_message(role, ai_response)

        # 대화 내용 저장은 이제 ai_chat.py에서 담당하므로 아래 로직은 주석 처리합니다.
        # user_input = self.last_user_input
        # if user_input and ai_response:
        #     self.store_conversation_async(user_input, ai_response)

    def store_conversation_async(self, user_input: str, ai_response: str):
        """대화 내용을 비동기적으로 메모리에 저장합니다."""
        
        async def do_store():
            try:
                content = f"User: {user_input}\\nAI: {ai_response}"
                metadata = {
                    "type": "conversation",
                    "user_input": user_input,
                    "gpt_response": ai_response,
                    "timestamp": datetime.now().isoformat()
                }
                
                # get_memory_manager_sync()를 통해 얻은 인스턴스를 사용
                success = await self.memory_manager.store_memory(content=content, metadata=metadata)
                if success:
                    # logger.info("대화 내용이 성공적으로 메모리에 저장되었습니다.")
                    pass
                else:
                    # logger.warning("대화 내용 메모리 저장에 실패했습니다.")
                    pass
            except Exception as e:
                # logger.error(f"대화 내용 저장 중 비동기 작업 오류: {e}", exc_info=True)
                pass

        add_task(asyncio.create_task(do_store()))

    def handle_error(self, error_message: str):
        QMessageBox.critical(self, "오류", f"AI 응답 처리 중 오류가 발생했습니다:\\n{error_message}")
        self.display_message("System", f"오류: {error_message}")

    def display_message(self, role: str, content: str, save_to_log: bool = True):
        timestamp = datetime.now().strftime("%H:%M")
        
        # HTML 표시를 위해 개행 문자를 <br>로 변환
        display_content = content.replace('\\n', '<br>')

        # HTML 템플릿
        # 사용자 메시지 템플릿
        user_template = f'''
        <div style="text-align: right; margin: 5px;">
            <p style="font-weight: bold; margin-bottom: 2px;">사용자</p>
            <div style="background-color: #dcf8c6; display: inline-block; padding: 10px; border-radius: 10px; max-width: 70%; text-align: left;">{display_content}</div>
            <div><span style="font-size: 9px; color: grey;">{timestamp}</span></div>
        </div>'''
        
        # AI 및 시스템 메시지 템플릿
        ai_template = f'''
        <div style="text-align: left; margin: 5px;">
            <p style="font-weight: bold; margin-bottom: 2px;">{role}</p>
            <div style="background-color: #f1f0f0; display: inline-block; padding: 10px; border-radius: 10px; max-width: 70%; text-align: left;">{display_content}</div>
            <div><span style="font-size: 9px; color: grey;">{timestamp}</span></div>
        </div>'''

        if role.lower() == "user":
            self._append_html_to_display(user_template)
        else:
            self._append_html_to_display(ai_template)
        
        if save_to_log:
            append_message(self.session_name, role, content)

    def _append_html_to_display(self, html: str):
        """주어진 HTML을 채팅창에 추가합니다."""
        self.chat_area.append(html)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def load_chat_history(self, session_name: str):
        """세션의 대화 기록(txt)을 불러와 화면에 표시합니다."""
        self.session_name = session_name
        self.chat_area.clear()
        
        messages = load_messages(session_name)
        if not messages:
            self.display_message("System", f"'{session_name}' 세션이 시작되었습니다. 메시지를 입력하세요.", save_to_log=False)
            return

        for role, content in messages:
            self.display_message(role, content, save_to_log=False)

    def load_file(self):
        """파일을 열어 내용을 입력창에 넣고 전송 준비"""
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "텍스트 파일 (*.txt *.py *.md);;모든 파일 (*.*)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.input_field.setPlainText(content)
                self.display_message("System", f"파일 '{os.path.basename(file_path)}'의 내용을 불러왔습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일을 읽는 중 오류가 발생했습니다:\n{e}")

    def clear_chat(self):
        """현재 세션의 대화 내용과 파일을 모두 지웁니다."""
        reply = QMessageBox.question(self, "대화 내용 삭제",
                                     f"'{self.session_name}'의 대화 내용을 정말로 지우시겠습니까? 파일 기록도 함께 삭제됩니다.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.chat_area.clear()
            # 채팅 로그 파일을 삭제합니다.
            delete_chat_log(self.session_name)
            # logger.info(f"'{self.session_name}'의 대화 내용이 삭제되었습니다.")
            self.display_message("System", "대화 내용이 삭제되었습니다.", save_to_log=False) 