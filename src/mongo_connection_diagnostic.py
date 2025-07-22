import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection(uri="mongodb://localhost:27017/aura_memory", timeout_ms=3000):
    print(f"🔍 MongoDB URI: {uri}")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        # 연결 테스트
        client.admin.command("ping")
        dbs = client.list_database_names()
        print("✅ MongoDB 연결 성공")
        print("📂 사용 가능한 데이터베이스 목록:", dbs)
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print("❌ MongoDB 연결 실패:", str(e))
        return False
    except Exception as e:
        print("❌ 예기치 않은 오류 발생:", str(e))
        return False

if __name__ == "__main__":
    test_mongodb_connection()