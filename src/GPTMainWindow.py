"""
GPT-4와 EORA(Embodied Oracle Agent)를 통합한 자동 개발 스튜디오

- PyQt5 기반 GUI
- 파일 탐색기, 코드 편집기, 로그 뷰어
- 채팅 기반 AI 상호작용
- 세션 관리
- EORA 엔진 연동
- 자동화 매크로, 에러 관리 등 확장 기능
"""
import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'EORA_Wisdom_Framework'))
from typing import Dict, Any, Optional
from datetime import datetime
from concurrent.futures import CancelledError

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeView, QFileSystemModel, QPushButton, QTextEdit,
    QLabel, QListWidget, QTabWidget, QMenu, QInputDialog, QMessageBox,
    QFileDialog
)
from PyQt5.QtCore import Qt, QDir, QThread, pyqtSignal, QTimer, QEvent
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QKeyEvent

from aura_system.ai_chat import get_eora_ai, load_existing_session
from aura_system.vector_store import embed_text_async
from aura_system.analysis import Analysis
from eora_chat_panel import GPTChatPanel
from eora_mini_manager_tab import EORAMiniManagerTab
from ProjectPlanningPanel import ProjectPlanningPanel
from AIManagerTab import AIManagerTab
from AIManagerMacroTab import AIManagerMacroTab
from error_notebook_ui_panel import EnhancedErrorNotebook
from EORA.eora_tab_with_subtabs import EORATab
from EORA.eora_learning_tab import EORALearningTab
from EORA.eora_memory_viewer import MemoryViewerTab as EORAMemoryViewer
from EORA.eora_file_analyzer import FileAnalyzerTab as EORAFileAnalyzerTab
from EORA import aura_memory_mongo as memory
from EORA_GAI.eai_launcher import initialize_eai

from gpt_worker import GPTWorker
from EORA_Wisdom_Framework.eora_engine import EORAEngine
from EORA import aura_core, ai2_reflector
from aura_system.memory_manager import MemoryManagerAsync, get_memory_manager_sync
from aura_system.task_manager import add_task, get_pending_tasks
from chat_session_manager import (
    append_message, load_messages, delete_chat_log,
    load_session_list, create_session, get_session_dir,
    get_session_list, create_new_session, delete_session
)
import shutil
import qasync
import asyncio
from EORA.eora_prompt_memory_dialogue_tab import EORAPromptMemoryDialogueTab
from eora_framework_tab import EORAFrameworkTab
from aura_system.task_manager import TaskManager
from aura_system.resource_manager import ResourceManager
from chat_session_manager import get_session_list, create_new_session, delete_session
from ai_chat_recall import perform_recall
from aura_system.recall_engine import RecallEngine

logger = logging.getLogger(__name__)

# ==============================================================================
# eora_chat_panel.py에서 가져온 클래스들
# ==============================================================================

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
            pass
        except Exception as e:
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
    tasks_created = pyqtSignal(list)
    send_user_input = pyqtSignal(str) # MainWindow로 사용자 입력을 전달하기 위한 시그널

    def __init__(self, session_name: str, eai_system: Any = None, parent=None):
        super().__init__(parent)
        self.session_name = session_name
        self.eai_system = eai_system
        self.memory_manager = get_memory_manager_sync()
        self.last_user_input = ""
        self.attached_file = None  # 첨부파일 경로 임시 저장
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
        
        self.send_button = QPushButton("전송")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        self.file_button = QPushButton("파일")
        self.file_button.clicked.connect(self.load_file)
        button_layout.addWidget(self.file_button)

        self.clear_button = QPushButton("지우기")
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)
        
        input_layout.addLayout(button_layout)
        layout.addLayout(input_layout)

    def send_message(self):
        user_input = self.input_field.toPlainText().strip()
        if not user_input:
            return
        # 첨부파일이 있으면 명령어에 따라 처리
        if self.attached_file:
            import asyncio
            from aura_system.file_loader import load_file_and_store_memory, split_text_into_chunks
            file_path = self.attached_file
            file_name = os.path.basename(file_path)
            # 명령어 분기
            if any(cmd in user_input for cmd in ["기억해", "학습", "학습자료", "저장해"]):
                try:
                    asyncio.create_task(self._async_store_file_and_notify(file_path, "기억에 저장"))
                    self.display_message("System", f"파일이 기억에 저장되었습니다: {file_name}")
                except Exception as e:
                    QMessageBox.critical(self, "오류", f"파일 저장 중 오류 발생: {e}")
            elif any(cmd in user_input for cmd in ["요약", "요약해"]):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    # 간단 요약(앞부분 200자)
                    summary = text[:200].replace('\n', ' ') + ("..." if len(text) > 200 else "")
                    self.display_message("System", f"[요약] {file_name}:\n{summary}")
                except Exception as e:
                    QMessageBox.critical(self, "오류", f"파일 요약 중 오류 발생: {e}")
            elif any(cmd in user_input for cmd in ["분석", "분석해"]):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    # 간단 분석(길이, 줄수, 키워드 등)
                    lines = text.splitlines()
                    words = text.split()
                    analysis = f"줄 수: {len(lines)}, 단어 수: {len(words)}, 길이: {len(text)}자"
                    self.display_message("System", f"[분석] {file_name}:\n{analysis}")
                except Exception as e:
                    QMessageBox.critical(self, "오류", f"파일 분석 중 오류 발생: {e}")
            elif any(cmd in user_input for cmd in ["코드 오류", "오류", "에러"]):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    # LLM API로 코드 오류 진단 요청 (간단 예시)
                    asyncio.create_task(self._async_code_error_check(file_name, code))
                except Exception as e:
                    QMessageBox.critical(self, "오류", f"코드 오류 진단 중 오류 발생: {e}")
            else:
                QMessageBox.information(self, "안내", "첨부파일이 있지만 명령어(예: '기억해', '요약해', '분석해', '학습자료', '코드 오류')가 포함되어야 파일이 처리됩니다.")
            self.attached_file = None
            self.input_field.clear()
            return
        # 첨부파일이 없으면 기존대로 동작
        # 4000자 청크 분할
        def split_text_into_chunks(text, max_length=4000):
            return [text[i:i+max_length] for i in range(0, len(text), max_length)]
        chunks = split_text_into_chunks(user_input, 4000)
        if len(chunks) == 1:
            self.display_message("User", user_input)
            self.input_field.clear()
            self.send_user_input.emit(user_input)
        else:
            self.display_message("User", f"[청크 분할 전송: 총 {len(chunks)}개]")
            self.input_field.clear()
            import asyncio
            async def send_chunks_parallel():
                from aura_system.ai_chat import get_eora_ai
                eora = await get_eora_ai()
                async def get_response(idx, chunk):
                    response = await eora.respond_async(chunk)
                    return idx, response.get("response", "")
                tasks = [get_response(idx, chunk) for idx, chunk in enumerate(chunks)]
                results = await asyncio.gather(*tasks)
                results.sort()  # 순서 보장
                for idx, resp in results:
                    self.display_message("User", f"[청크 {idx+1}/{len(chunks)}] {chunks[idx]}", save_to_log=False)
                    self.display_message("assistant", resp, save_to_log=False)
                # 전체 합친 응답을 한 번에 출력(선택)
                # self.display_message("assistant", f"[전체 응답] {''.join([r for _, r in results])}", save_to_log=False)
            asyncio.create_task(send_chunks_parallel())

    async def _async_store_file_and_notify(self, file_path, mode):
        from aura_system.file_loader import load_file_and_store_memory
        try:
            await load_file_and_store_memory(file_path)
            # 대화창 출력은 send_message에서 처리
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 처리 중 오류 발생: {e}")

    async def _async_code_error_check(self, file_name, code):
        try:
            from openai import AsyncOpenAI
            import os
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            prompt = f"아래 코드를 분석해서 오류, 버그, 개선점을 알려줘.\n\n코드:\n{code}"
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "너는 코드 분석 전문가다."}, {"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content
            self.display_message("System", f"[코드 오류 진단] {file_name}:\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"코드 오류 진단 중 오류 발생: {e}")

    def handle_response(self, response: Dict[str, Any]):
        role = response.get("role", "AI")
        ai_response = response.get("response", "응답이 없습니다.")
            
        self.display_message(role, ai_response)

    def store_conversation_async(self, user_input: str, ai_response: str):
        async def do_store():
            try:
                content = f"User: {user_input}\\nAI: {ai_response}"
                metadata = {
                    "type": "conversation",
                    "user_input": user_input,
                    "gpt_response": ai_response,
                    "timestamp": datetime.now().isoformat()
                }
                success = await self.memory_manager.store_memory(content=content, metadata=metadata)
                if success:
                    pass
                else:
                    pass
            except Exception as e:
                pass
        add_task(asyncio.create_task(do_store()))

    def handle_error(self, error_message: str):
        QMessageBox.critical(self, "오류", f"AI 응답 처리 중 오류가 발생했습니다:\\n{error_message}")
        self.display_message("System", f"오류: {error_message}")

    def display_message(self, role: str, content: str, save_to_log: bool = True):
        timestamp = datetime.now().strftime("%H:%M")
        display_content = content.replace('\\n', '<br>')
        user_template = f'''
        <div style="text-align: right; margin: 5px;">
            <p style="font-weight: bold; margin-bottom: 2px;">사용자</p>
            <div style="background-color: #dcf8c6; display: inline-block; padding: 10px; border-radius: 10px; max-width: 70%; text-align: left;">{display_content}</div>
            <div><span style="font-size: 9px; color: grey;">{timestamp}</span></div>
        </div>'''
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
        self.chat_area.append(html)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
        # setPosition 호출 완전히 제거 (PyQt 경고 방지)

    def load_chat_history(self, session_name: str):
        self.session_name = session_name
        self.chat_area.clear()
        
        messages = load_messages(session_name)
        if not messages:
            self.display_message("System", f"'{session_name}' 세션이 시작되었습니다. 메시지를 입력하세요.", save_to_log=False)
            return

        for role, content in messages:
            self.display_message(role, content, save_to_log=False)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "텍스트 파일 (*.txt *.py *.md);;모든 파일 (*.*)")
        if file_path:
            self.attached_file = file_path
            file_name = os.path.basename(file_path)
            self.display_message("System", f"파일이 첨부되었습니다: {file_name}")
            QMessageBox.information(self, "첨부 완료", f"{file_name} 파일이 첨부되었습니다.\n명령어(예: '기억해', '요약해', '분석해', '학습자료')와 함께 전송하면 해당 파일이 처리됩니다.")

    def clear_chat(self):
        try:
            reply = QMessageBox.question(self, '대화 내용 삭제',
                                         f"'{self.session_name}' 세션의 대화 기록을 정말로 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    delete_chat_log(self.session_name)
                except Exception as e:
                    QMessageBox.critical(self, "오류", f"대화 기록 삭제 중 오류 발생: {e}")
                    return
                self.chat_area.clear()
                self.display_message("System", f"'{self.session_name}' 세션의 대화 기록이 삭제되었습니다.", save_to_log=False)
                # 삭제 후 남은 메시지가 없으면 추가 갱신 금지
                messages = load_messages(self.session_name)
                if not messages:
                    return
        except Exception as e:
            QMessageBox.critical(self, "오류", f"대화 내용 삭제 중 예외 발생: {e}")

    def set_session(self, name):
        self.session_name = name
        self.load_chat_history(name)

# ==============================================================================


class GPTMainWindow(QMainWindow):
    """GPT 메인 윈도우"""
    
    def __init__(self, memory_manager, eora=None):
        """GPT 메인 윈도우"""
        super().__init__()
        self.memory_manager = memory_manager
        if self.memory_manager is None:
            raise RuntimeError("MemoryManager가 초기화되지 않은 상태로 GPTMainWindow에 전달되었습니다.")

        # EAI 시스템 초기화
        self.eai_system = initialize_eai()
        if self.eai_system:
            pass  # logging.info("✅ EAI 시스템이 성공적으로 초기화되었습니다.")
        else:
            pass  # logging.warning("⚠️ EAI 시스템 초기화에 실패했습니다.")

        self.eora = eora
        self.eora_engine = EORAEngine(memory_manager=self.memory_manager)
        self.shutdown_future = None # 종료 신호를 위한 Future 객체
        
        self.setWindowTitle("EORA GPT CHAT")
        self.setMinimumSize(1440, 900)
        load_existing_session()
        
        try:
            # UI 초기화
            self.tree = QTreeView()
            self.tree_model = QFileSystemModel()
            self.tree_model.setRootPath(QDir.rootPath())
            self.tree.setModel(self.tree_model)
            self.tree.setRootIndex(self.tree_model.index(QDir.rootPath()))
            self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree.customContextMenuRequested.connect(self.tree_context_menu)
            self.tree.doubleClicked.connect(self.tree_double_click)

            self.code_view = QTextEdit()
            self.log_view = QTextEdit()
            self.log_view.setReadOnly(True)

            tree_btns = QHBoxLayout()
            btn_add_file = QPushButton("📄 새 파일")
            btn_add_folder = QPushButton("📁 새 폴더")
            btn_delete = QPushButton("🗑️ 삭제")
            btn_add_file.clicked.connect(lambda: self.create_text_file(self.get_selected_path()))
            btn_add_folder.clicked.connect(lambda: self.create_folder(self.get_selected_path()))
            btn_delete.clicked.connect(lambda: self.delete_item(self.get_selected_path()))
            tree_btns.addWidget(btn_add_file)
            tree_btns.addWidget(btn_add_folder)
            tree_btns.addWidget(btn_delete)

            code_btns = QHBoxLayout()
            btn_run = QPushButton("▶ 실행")
            btn_save = QPushButton("💾 저장")
            btn_copy = QPushButton("📋 복사")
            btn_undo = QPushButton("↩ 되돌리기")
            btn_run.clicked.connect(self.run_code)
            btn_save.clicked.connect(self.save_code)
            btn_copy.clicked.connect(self.copy_code)
            btn_undo.clicked.connect(self.code_view.undo)
            code_btns.addWidget(btn_run)
            code_btns.addWidget(btn_save)
            code_btns.addWidget(btn_copy)
            code_btns.addWidget(btn_undo)

            file_layout = QVBoxLayout()
            file_layout.addWidget(QLabel("📂 파일 탐색기"))
            file_layout.addWidget(self.tree)
            file_layout.addLayout(tree_btns)
            file_layout.addWidget(QLabel("💻 코드 편집기"))
            file_layout.addWidget(self.code_view)
            file_layout.addLayout(code_btns)
            file_layout.addWidget(QLabel("📜 로그"))
            file_layout.addWidget(self.log_view)
            file_panel = QWidget()
            file_panel.setLayout(file_layout)
            file_panel.setMinimumWidth(400)

            self.session_list = QListWidget()
            self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.session_list.customContextMenuRequested.connect(self.handle_session_context_menu)
            btn_add = QPushButton("➕ 세션 추가")
            btn_del = QPushButton("🗑️ 세션 삭제")
            btn_add.clicked.connect(self.add_session)
            btn_del.clicked.connect(self.del_session)
            session_layout = QVBoxLayout()
            session_layout.addWidget(QLabel("💾 세션 목록"))
            session_layout.addWidget(self.session_list)
            sbtns = QHBoxLayout()
            sbtns.addWidget(btn_add)
            sbtns.addWidget(btn_del)
            session_layout.addLayout(sbtns)
            session_panel = QWidget()
            session_panel.setLayout(session_layout)
            session_panel.setMinimumWidth(200)

            self.tabs = QTabWidget()
            chat_panel = GPTChatPanel(session_name="기본 세션")
            chat_panel.send_user_input.connect(self.run_gpt_worker) # 시그널 연결
            self.tabs.addTab(chat_panel, "💬 EORA 대화")
            self.tabs.addTab(EORATab(log_panel=self.log_view), "🌌 EORA")
            self.tabs.addTab(AIManagerTab(), "🧠 AI 관리")
            self.tabs.addTab(ProjectPlanningPanel(), "📌 프로젝트 기획")
            self.tabs.addTab(AIManagerMacroTab(global_logger=self.log_view), "🔧 매크로 자동화")
            self.tabs.addTab(EnhancedErrorNotebook(), "📘 에러관리")
            self.tabs.addTab(EORAMiniManagerTab(), "🧠 이오라 코어")

            # EORA 프롬프트/메모리 다이얼로그 탭 추가
            self.eora_tab = EORAPromptMemoryDialogueTab(self)
            self.tabs.addTab(self.eora_tab, "EORA 다이얼로그")

            # EORA 프레임워크 탭 추가 및 비동기 초기화
            self.eora_framework_tab = EORAFrameworkTab()
            asyncio.create_task(self.eora_framework_tab.initialize_ai())
            self.tabs.addTab(self.eora_framework_tab, "EORA Framework")

            splitter = QSplitter(Qt.Horizontal)
            splitter.addWidget(file_panel)
            splitter.addWidget(session_panel)
            splitter.addWidget(self.tabs)

            layout = QVBoxLayout()
            container = QWidget()
            container.setLayout(layout)
            layout.addWidget(splitter)
            self.setCentralWidget(container)
            
            # EAI 초기화 로그 추가
            if self.eai_system:
                self.log_view.append("✅ EAI 시스템이 성공적으로 초기화되었습니다.")
                self.log_view.append(str(self.eai_system.describe()))
            else:
                self.log_view.append("❌ EAI 시스템 초기화에 실패했습니다.")

            # EORA 초기화
            self.log_view.append(self.eora_engine.reflect_existence())
            self.log_view.append(self.eora_engine.truth_summary())
            self.log_view.append("🔄 EORA 회상 시스템 초기화 중...")
            self.log_view.append(self.eora_engine.reflect_memories())
            
            # 기본 세션이 없으면 생성
            if "기본 세션" not in load_session_list():
                create_session("기본 세션")

            self.refresh_session_list()  # 세션 목록을 항상 폴더 기준으로 UI에 반영
            
            self.session_list.currentTextChanged.connect(self.on_session_changed)
            
            # 새로운 속성 추가
            self.recall_engine = RecallEngine(self.memory_manager)
            
        except Exception as e:
            logger.error(f"메인 윈도우 초기화 실패: {str(e)}")
            raise RuntimeError(f"메인 윈도우 초기화 실패: {str(e)}")

    def tree_context_menu(self, pos):
        path = self.get_selected_path()
        menu = QMenu(self)
        menu.addAction("📄 새 파일", lambda: self.create_text_file(path))
        menu.addAction("📁 새 폴더", lambda: self.create_folder(path))
        menu.addAction("🗑️ 삭제", lambda: self.delete_item(path))
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def tree_double_click(self, index):
        path = self.get_selected_path()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                self.code_view.setPlainText(f.read())

    def get_selected_path(self):
        index = self.tree.currentIndex()
        return self.tree_model.filePath(index)

    def run_code(self):
        path = self.get_selected_path()
        if os.path.isfile(path) and path.endswith(".py"):
            os.system(f'start cmd /K "python "{path}\""')

    def save_code(self):
        path = self.get_selected_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.code_view.toPlainText())
        self.log_view.append(f"✅ 저장됨: {path}")

    def copy_code(self):
        QApplication.clipboard().setText(self.code_view.toPlainText())

    def create_text_file(self, folder):
        name, ok = QInputDialog.getText(self, "파일 이름", "입력:")
        if ok:
            path = os.path.join(folder, name if name.endswith(".txt") else name + ".txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            self.log_view.append(f"📄 생성됨: {path}")

    def create_folder(self, folder):
        name, ok = QInputDialog.getText(self, "폴더 이름", "입력:")
        if ok:
            os.makedirs(os.path.join(folder, name), exist_ok=True)
            self.log_view.append(f"📁 생성됨: {os.path.join(folder, name)}")

    def delete_item(self, path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.log_view.append(f"🗑️ 삭제됨: {path}")
        except Exception as e:
            self.log_view.append(f"❌ 삭제 실패: {e}")

    def handle_session_context_menu(self, pos):
        item = self.session_list.itemAt(pos)
        if item:
            menu = QMenu(self)
            rename = menu.addAction("✏️ 이름 수정")
            delete = menu.addAction("🗑️ 삭제")
            act = menu.exec_(self.session_list.mapToGlobal(pos))
            if act == rename:
                new, ok = QInputDialog.getText(self, "세션 이름 변경", "입력:", text=item.text())
                if ok and new:
                    # 세션 이름 변경 로직 (향후 구현)
                    old_session_dir = get_session_dir(item.text())
                    new_session_dir = get_session_dir(new)
                    try:
                        if os.path.exists(new_session_dir):
                            QMessageBox.warning(self, "오류", "같은 이름의 세션이 이미 존재합니다.")
                            return
                        os.rename(old_session_dir, new_session_dir)
                        item.setText(new)
                        self.log_view.append(f"세션 이름이 '{item.text()}'에서 '{new}'(으)로 변경되었습니다.")
                        # 현재 탭의 세션 이름도 업데이트
                        current_widget = self.tabs.currentWidget()
                        if isinstance(current_widget, GPTChatPanel) and current_widget.session_name == item.text():
                            current_widget.session_name = new
                    except Exception as e:
                        QMessageBox.critical(self, "오류", f"세션 이름 변경 실패: {e}")
                        logger.error(f"세션 이름 변경 실패: {e}", exc_info=True)
            elif act == delete:
                self.del_session()

    def add_session(self):
        session_name, ok = QInputDialog.getText(self, "새 세션", "세션 이름을 입력하세요:")
        if ok and session_name:
            if create_session(session_name):
                self.refresh_session_list()
                self.log_view.append(f"세션 '{session_name}' 추가됨")
            else:
                QMessageBox.warning(self, "오류", f"세션 '{session_name}'을(를) 생성하지 못했습니다.")

    def del_session(self):
        item = self.session_list.currentItem()
        if not item:
            QMessageBox.warning(self, "오류", "삭제할 세션을 선택하세요.")
            return

        session_name = item.text()
        reply = QMessageBox.question(self, '세션 삭제', f"'{session_name}' 세션을 정말 삭제하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                session_dir = get_session_dir(session_name)
                shutil.rmtree(session_dir)
                self.refresh_session_list()
                self.log_view.append(f"세션 '{session_name}' 삭제됨")
            except Exception as e:
                QMessageBox.warning(self, "오류", f"세션 삭제 중 오류 발생: {e}")
                logger.error(f"세션 삭제 실패: {e}", exc_info=True)

    def on_session_changed(self, name):
        """세션 변경 시 호출"""
        if not name:
            return

        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, GPTChatPanel):
            current_widget.set_session(name)
            self.log_view.append(f"🔄 세션 변경: {name}")

    @qasync.asyncSlot(str)
    async def run_gpt_worker(self, user_input: str):
        # print("[GPTMainWindow.run_gpt_worker] 진입", user_input)
        current_widget = self.tabs.currentWidget()
        if not isinstance(current_widget, GPTChatPanel):
            self.log_view.append("⚠️ 활성 탭이 채팅 패널이 아닙니다.")
            return

        QApplication.processEvents()

        # 회상 결과를 대화창에 출력하지 않도록 완전히 제거
        recall_context = None
        try:
            recall_context = await self.recall_engine.recall(user_input)
        except Exception as e:
            self.log_view.append(f"❌ 회상 호출 오류: {e}")

        try:
            from aura_system.ai_chat import get_eora_ai
            from aura_system.memory_manager import get_memory_manager
            eora = await get_eora_ai()
            memory_manager = await get_memory_manager()
            response = await eora.respond_async(
                user_input=user_input,
                recall_context=recall_context  # 회상 결과를 전달
            )
            await memory_manager.store_memory(
                content=user_input,
                metadata={
                    "type": "user_input",
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            self.on_gpt_response(response)
        except Exception as e:
            self.log_view.append(f"❌ EORA 응답 생성 오류: {e}")
            current_widget.display_message("system", f"오류: {e}")

    def on_gpt_response(self, response: Dict[str, Any]):
        """GPT 응답 처리"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, GPTChatPanel):
            if response.get("error"):
                current_widget.display_message("system", f"오류: {response['error']}")
            else:
                current_widget.display_message("assistant", response["response"])

    def load_sessions(self):
        self.session_list.clear()
        for session_name in load_session_list():
            self.session_list.addItem(session_name)

    def set_shutdown_future(self, future: asyncio.Future):
        """애플리케이션 종료 신호를 위한 Future 객체를 설정합니다."""
        self.shutdown_future = future

    def closeEvent(self, event):
        """윈도우가 닫힐 때 호출되는 이벤트 핸들러"""
        if self.shutdown_future and not self.shutdown_future.done():
            self.shutdown_future.set_result(True)
        # 비동기 정리 보장
        try:
            if hasattr(self, '_await_pending_tasks'):
                asyncio.ensure_future(self._await_pending_tasks())
        except Exception as e:
            logger.error(f"비동기 정리 작업 중 오류: {e}")
        super().closeEvent(event)

    def _add_background_tasks(self, tasks: list):
        """
        백그라운드에서 실행될 비동기 태스크 목록을 중앙 관리 시스템에 추가합니다.
        추가된 태스크들은 완료되면 자동으로 목록에서 제거됩니다.
        """
        for task in tasks:
            add_task(task)

    def refresh_session_list(self):
        """세션 목록 UI를 새로고침합니다."""
        self.session_list.clear()
        sessions = load_session_list()
        self.session_list.addItems(sessions) 