
import subprocess
import threading
import time
import os

def run_backend():
    print("🚀 EORA 백엔드 실행 중... (http://127.0.0.1:8600)")
    subprocess.call(["uvicorn", "eora_backend:app", "--host", "127.0.0.1", "--port", "8600", "--reload"])

def run_frontend():
    time.sleep(2)  # 백엔드보다 2초 늦게 시작
    print("🌈 EORA 학습 앱 실행 중... (http://localhost:8501)")
    subprocess.call(["streamlit", "run", "eora_learning_app.py"])

if __name__ == "__main__":
    os.system("title EORA SYSTEM LAUNCHER")
    threading.Thread(target=run_backend).start()
    threading.Thread(target=run_frontend).start()
