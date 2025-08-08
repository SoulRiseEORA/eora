def build_learning_tab(self):
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

    tab = QWidget()
    layout = QVBoxLayout(tab)
    label = QLabel("📘 학습 루프 패널이 준비 중입니다.")
    layout.addWidget(label)
    return tab


def build_memory_tab(self):
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

    tab = QWidget()
    layout = QVBoxLayout(tab)
    label = QLabel("🧠 메모리 뷰어 패널이 준비 중입니다.")
    layout.addWidget(label)
    return tab


def build_analyzer_tab(self):
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

    tab = QWidget()
    layout = QVBoxLayout(tab)
    label = QLabel("📂 파일 분석기 패널이 준비 중입니다.")
    layout.addWidget(label)
    return tab


def build_chat_tab(self):
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

    tab = QWidget()
    layout = QVBoxLayout(tab)
    label = QLabel("💬 GPT 대화 탭이 준비 중입니다.")
    layout.addWidget(label)
    return tab