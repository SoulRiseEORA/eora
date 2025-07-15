
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import pyqtSignal, Qt

class ChatInputArea(QPlainTextEdit):
    send_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setPlaceholderText("메시지를 입력하세요...")
        self.setFixedHeight(100)
        self.setStyleSheet("""
            border: 2px solid #888;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        """)

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Return:
                if event.modifiers() & Qt.ShiftModifier:
                    self.insertPlainText("\n")
                else:
                    text = self.toPlainText().strip()
                    if text:
                        try:
                            self.send_message.emit(text)
                        except Exception as emit_error:
                            print("[전송 이벤트 오류]", emit_error)
                        self.clear()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print("[입력 오류]", e)
