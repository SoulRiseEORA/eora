from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser

class ErrorNotebook(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.text_browser = QTextBrowser()
        layout.addWidget(self.text_browser)

    def record_error(self, error_text, related_input=None):
        entry = f"[ERROR] {error_text}"
        if related_input:
            entry += f"  ▶ 관련 입력: {related_input}"
        self.text_browser.append(entry)