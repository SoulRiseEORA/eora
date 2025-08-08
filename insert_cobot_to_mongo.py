
from pymongo import MongoClient
import pandas as pd

# MongoDB 연결 설정 (로컬 PC에서 실행)
client = MongoClient("mongodb://localhost:27017/")
db = client["eora_ai"]
collection = db["cobot_features"]

# 기존 데이터 삭제 (선택 사항)
collection.delete_many({})

# 엑셀 파일 읽기
df = pd.read_excel("코봇_기능_6000개_점수정밀최종.xlsx")
df = df.dropna(subset=[df.columns[0]])
df.columns = [f"col_{i}" if not col else col for i, col in enumerate(df.columns)]

# Mongo에 삽입
collection.insert_many(df.to_dict(orient="records"))

print("✅ MongoDB에 총", len(df), "개 항목 삽입 완료")
