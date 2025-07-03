
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QTextCursor
import markdown2
from PyQt5.QtWidgets import QMessageBox

class ChatDisplay(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setOpenExternalLinks(False)
        self.anchorClicked.connect(self.on_anchor_clicked)

    def append_markdown(self, markdown_text):
        try:
            html = markdown2.markdown(markdown_text)
            self.moveCursor(QTextCursor.End)
            self.insertHtml(html)
            self.insertPlainText("\n\n")
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

            # 안전한 미리보기 로그
            for seg in markdown_text.split("```"):
                if seg.strip():
                    preview = seg.splitlines()[0][:15] + "..."
                else:
                    preview = "..."
                break
        except Exception as e:
            QMessageBox.critical(self, "마크다운 처리 오류", str(e))

    def on_anchor_clicked(self, url: QUrl):
        QMessageBox.information(self, "링크 클릭됨", f"클릭한 링크: {url.toString()}")
