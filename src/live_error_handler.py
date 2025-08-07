
from datetime import datetime

class LiveErrorHandler:
    def __init__(self, table_widget):
        self.table = table_widget

    def report(self, error_message, file_name, tab_name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(error_message))
        self.table.setItem(row, 1, QTableWidgetItem(file_name))
        self.table.setItem(row, 2, QTableWidgetItem(tab_name))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.table.setItem(row, 3, QTableWidgetItem(now))
