
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton
from EORA.eora_memory_log_viewer import EmotionMemoryLogViewer
from EORA.eora_journal_viewer import EORAJournalViewer
from EORA.eora_prompt_storage_viewer import PromptStorageViewer

class RecordTabs(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tabset = QTabWidget()

        tabset.addTab(PromptStorageViewer(), "📦 저장소")
        tabset.addTab(EmotionMemoryLogViewer(), "💬 감정 / 기억")
        tabset.addTab(EORAJournalViewer(), "📓 저널")

        layout.addWidget(tabset)
        self.setLayout(layout)
