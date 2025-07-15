#!/usr/bin/env python3
"""
🚀 Railway 간단 시작 스크립트
- main.py 완전 무시
- app.py만 실행
- 최소한의 코드로 최대 안정성
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    print("🚀 Railway 간단 서버 시작...")
    
    # 포트 설정
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    
    # main.py 파일 임시 이름 변경
    main_file = Path("main.py")
    if main_file.exists():
        try:
            main_file.rename("main_disabled.py")
            print("✅ main.py를 main_disabled.py로 변경")
        except:
            print("⚠️ main.py 이름 변경 실패")
    
    # app.py import 및 실행
    try:
        import app
        print("✅ app.py 로드 성공")
        
        uvicorn.run(
            app.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False
        )
    except Exception as e:
        print(f"❌ 오류: {e}")
        # main.py 복원
        disabled_file = Path("main_disabled.py")
        if disabled_file.exists():
            try:
                disabled_file.rename("main.py")
                print("✅ main.py 복원 완료")
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main() 