from PyQt5.QtWidgets import QTextEdit, QLineEdit

def create_text_log():
    log = QTextEdit()
    log.setReadOnly(True)
    return log

def create_input_line():
    input_field = QLineEdit()
    input_field.setPlaceholderText("👤 사용자 응답 또는 /첨부:파일명 입력")
    return input_field
