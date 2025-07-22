import os
import sys

print("="*60)
print("진단 스크립트가 성공적으로 실행되었습니다.")
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"이 스크립트의 절대 경로: {os.path.abspath(__file__)}")
print("="*60) 