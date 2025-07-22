
from pymongo import MongoClient
from datetime import datetime

class ErrorLogger:
    def __init__(self, db_name='EORA', collection_name='error_notes', uri='mongodb://localhost:27017/'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def log_error(self, error_message, file_name, tab_name="미지정", repeat_count=1):
        doc = {
            "error": error_message,
            "file": file_name,
            "tab": tab_name,
            "timestamp": datetime.now(),
            "repeat": repeat_count
        }
        self.collection.insert_one(doc)
        print(f"✅ 에러 저장됨: {error_message} (파일: {file_name}, 탭: {tab_name}, 회차: {repeat_count})")

# 사용 예시 (테스트용)
if __name__ == "__main__":
    logger = ErrorLogger()
    logger.log_error(
        error_message="ZeroDivisionError: division by zero",
        file_name="calculator.py",
        tab_name="수식 엔진",
        repeat_count=1
    )
