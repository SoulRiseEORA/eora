"""
장기 감정 타임라인 분석기
- MongoDB memory_atoms에서 감정 흐름 추출
- 주 단위/월 단위 감정 변화 분석
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def fetch_emotion_data():
    memories = list(collection.find({}, {"timestamp": 1, "emotion_label": 1}))
    records = []
    for mem in memories:
        ts = mem.get("timestamp")
        label = mem.get("emotion_label", "기타")
        if ts:
            records.append({"timestamp": pd.to_datetime(ts), "emotion": label})
    return pd.DataFrame(records)

def plot_emotion_timeline(time_unit="W"):
    """
    time_unit: 'D' (day), 'W' (week), 'M' (month) 가능
    """
    df = fetch_emotion_data()
    if df.empty:
        print("⚠️ 감정 데이터가 없습니다.")
        return

    df.set_index("timestamp", inplace=True)
    emotion_counts = df.resample(time_unit).emotion.value_counts().unstack().fillna(0)

    plt.figure(figsize=(12,6))
    emotion_counts.plot(kind="area", stacked=True, alpha=0.7)
    plt.title(f"EORA 감정 타임라인 ({time_unit} 단위)")
    plt.xlabel("시간")
    plt.ylabel("감정 발생 수")
    plt.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_emotion_timeline("W")