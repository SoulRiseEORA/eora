""" run_ai_dev_tool.py - 진입점 """
import sys
import os
from PyQt5.QtWidgets import QApplication
from GPTMainWindow import GPTMainWindow
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

def main():
    app = QApplication(sys.argv)
    window = GPTMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
