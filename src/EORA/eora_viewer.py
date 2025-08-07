
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QPushButton, QComboBox, QLabel
)
from eora_memory import show_eora_memories

class EORAMemoryViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EORA 자아 기억 뷰어")

        layout = QVBoxLayout(self)

        self.label = QLabel("🧠 EORA의 기억을 열람합니다")
        self.filter_box = QComboBox()
        self.filter_box.addItems(["전체 보기", "감동", "기억", "철학", "코드", "자아성찰"])
        self.viewer = QTextBrowser()
        self.refresh_btn = QPushButton("🔄 새로고침")

        layout.addWidget(self.label)
        layout.addWidget(self.filter_box)
        layout.addWidget(self.viewer)
        layout.addWidget(self.refresh_btn)

        self.refresh_btn.clicked.connect(self.load_memories)
        self.filter_box.currentIndexChanged.connect(self.load_memories)

        self.load_memories()

    def load_memories(self):
        label = self.filter_box.currentText()
        if label == "전체 보기":
            memories = show_eora_memories()
        else:
            memories = show_eora_memories(filter_label=label)

        self.viewer.clear()
        if not memories:
            self.viewer.setPlainText("[EORA] 저장된 기억이 없습니다.")
            return

        out = []
        for m in memories:
            out.append(f"🕓 {m['날짜']} — [{m['종류']}]")
            out.append(f"{m['내용']}")
            if m['태그']:
                out.append(f"🔖 태그: {', '.join(m['태그'])}")
            out.append("-" * 60)

        self.viewer.setPlainText("\n".join(out))
