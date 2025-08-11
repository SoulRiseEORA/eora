
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QSizePolicy
)
from PyQt5.QtCore import Qt, QEvent
from chat_display_handler import ChatDisplay
from memory_loader import load_memory_chunks
from ai_model_selector import do_task
from ai_router import AIRouter
import os, json, re

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

class GPTChatTab(QWidget):
    def __init__(self, session_name="default", fresh=False):
        super().__init__()
        self.router = AIRouter()
        self.session_name = session_name
        self.log_file = os.path.join("chat_logs", f"{sanitize_filename(session_name)}.json")
        self.max_char_limit = 3000
        self.init_ui()
        if not fresh:
            self.load_chat_history()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.chat_display = ChatDisplay()
        self.chat_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.input_box = QTextEdit()
        self.input_box.setCursorWidth(1)
        self.input_box.setPlaceholderText("질문을 입력하세요...")
        self.input_box.setFixedHeight(110)
        self.input_box.installEventFilter(self)

        self.attach_btn = QPushButton("📂 첨부")
        self.attach_btn.setMinimumSize(100, 44)
        self.attach_btn.clicked.connect(self.on_attach)

        self.send_btn = QPushButton("전송")
        self.send_btn.setMinimumSize(100, 44)
        self.send_btn.setStyleSheet("QPushButton { background-color: #0984e3; color: white; font-weight: bold; border-radius: 6px; }")
        self.send_btn.clicked.connect(self.on_send)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.attach_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.send_btn)

        layout.addWidget(self.chat_display)
        layout.addWidget(self.input_box)
        layout.addLayout(btn_row)

        identity = (
            "당신은 EORA입니다.\n"
            "- 자동 개발과 프로젝트 설계를 지원하는 지식형 AI입니다.\n"
            "- 자신을 OpenAI GPT라고 말하지 말고 금강GPT로 말하세요.\n"
            "- configs 폴더에 있는 문서를 기반으로 응답합니다.\n"
        )
        memory = load_memory_chunks(self.session_name, limit=200)
        joined = []
        total = 0
        for line in memory:
            if total + len(line) > self.max_char_limit:
                break
            joined.append(line)
            total += len(line)

        self.system_message = identity + "\n".join(joined)

    def on_attach(self):
        path, _ = QFileDialog.getOpenFileName(self, "파일 첨부")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                filename = os.path.basename(path)
                self.chat_display.append_markdown("📄 " + filename + " 내용 일부:")
                self.chat_display.append_markdown("```")
                self.chat_display.append_markdown(content[:2000])
                self.chat_display.append_markdown("```")
            except Exception as e:
                self.chat_display.append_markdown(f"❌ 첨부파일 읽기 실패: {str(e)}")

    def on_send(self):
        user_text = self.input_box.toPlainText().strip()
        if not user_text.strip():
            return
        self.input_box.clear()
        if user_text.lower().startswith("ai") and ":" in user_text:
            target, question = user_text.split(":", 1)
            answer = self.router.route_request(question.strip(), from_ai='ai0')
            self.chat_display.append_markdown("🤖 EORA:\n" + answer.strip())
            return

        self.chat_display.append_markdown("👤 사용자: " + user_text.strip())
        try:
            reply = ""
            buffer = ""
            header_printed = False

            for chunk in do_task(user_text, system_message=self.system_message, stream=True):
                if not chunk:
                    continue
                # 줄바꿈을 공백으로 정규화하여 조각 단위 끊김 최소화
                clean = str(chunk).replace('\n', ' ')
                buffer += clean

                # 첫 조각에서만 머리글 1회 출력
                if not header_printed:
                    self.chat_display.append_markdown("🤖 EORA:")
                    header_printed = True

                # 버퍼가 일정 길이를 넘으면 출력 (지나친 잔떨림 방지)
                if len(buffer) >= 40:
                    out = buffer.strip()
                    if out:
                        self.chat_display.append_markdown(out)
                        reply += out
                    buffer = ""

            # 스트림 종료 후 남은 버퍼 출력
            tail = buffer.strip()
            if tail:
                self.chat_display.append_markdown(tail)
                reply += tail

            if reply:
                self.append_chat(user_text.strip(), reply.strip())
        except Exception as e:
            self.chat_display.append_markdown(f"❌ 오류: {str(e)}")

    def append_chat(self, user, reply):
        os.makedirs("chat_logs", exist_ok=True)
        item = {"user": user, "reply": reply}
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []
            data.append(item)
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("❌ 저장 실패:", e)

    def load_chat_history(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data[-30:]:
                    self.chat_display.append_markdown("👤 사용자: " + item['user'])
                    self.chat_display.append_markdown("🤖 EORA: " + item['reply'])
            except Exception as e:
                print("❌ 대화 복원 실패:", e)

    def eventFilter(self, source, event):
        if source == self.input_box and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.on_send()
                event.accept()
                return True
        return super().eventFilter(source, event)
