from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal

class EORAPromptMemoryDialogueTab(QWidget):
    # This signal can be used to notify other parts of the application
    # about updates or events happening in this tab.
    # For example, when a new memory is created or a dialogue is processed.
    update_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout for this tab
        layout = QVBoxLayout()

        # Text area to display prompt, memory, and dialogue information
        self.dialogue_view = QTextEdit()
        self.dialogue_view.setReadOnly(True)  # Make it non-editable by the user
        self.dialogue_view.setPlaceholderText("프롬프트, 메모리, 대화 내용이 여기에 표시됩니다...")

        # Add the text area to the layout
        layout.addWidget(self.dialogue_view)

        # Set the layout for the tab
        self.setLayout(layout)

    def display_content(self, content):
        """
        Updates the text area with new content.
        This could be called from the main application logic to show
        real-time data from the EORA system.
        """
        self.dialogue_view.append(content)
        self.update_signal.emit(f"Displayed content: {content[:50]}...")

    def clear_content(self):
        """
        Clears the text area.
        """
        self.dialogue_view.clear()
        self.update_signal.emit("Content cleared.")
