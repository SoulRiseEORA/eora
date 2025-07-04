#!/usr/bin/env python3
"""
EORA AI Railway 배포용 서버
환경변수 자동 수정 및 MongoDB 연결 안정화
"""

import os
import sys
import re
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 환경변수 자동 수정 함수
def fix_environment_variables():
    """환경변수 값을 자동으로 정리하고 수정"""
    
    # MongoDB 관련 환경변수들
    mongo_vars = [
        "MONGO_PUBLIC_URL",
        "MONGO_URL", 
        "MONGO_INITDB_ROOT_PASSWORD",
        "MONGO_INITDB_ROOT_USERNAME"
    ]
    
    for var_name in mongo_vars:
        value = os.getenv(var_name, "")
        if value:
            # 값 정리 (쌍따옴표, 공백, 줄바꿈 제거)
            cleaned_value = value.strip().replace('"', '').replace("'", "").replace('\n', '').replace('\r', '')
            
            # URL인 경우 추가 정리
            if var_name in ["MONGO_PUBLIC_URL", "MONGO_URL"] and cleaned_value.startswith("mongodb://"):
                # 포트 뒤에 다른 환경변수가 붙어있는 경우 수정
                if 'MONGO_INITDB_ROOT_PASSWORD=' in cleaned_value:
                    # 포트 번호까지만 추출
                    port_match = re.search(r':(\d+)', cleaned_value)
                    if port_match:
                        port = port_match.group(1)
                        # trolley.proxy.rlwy.net:포트까지만 사용
                        if 'trolley.proxy.rlwy.net' in cleaned_value:
                            password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "").strip().replace('"', '').replace("'", "")
                            cleaned_value = f"mongodb://mongo:{password}@trolley.proxy.rlwy.net:{port}"
                        elif 'mongodb.railway.internal' in cleaned_value:
                            password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "").strip().replace('"', '').replace("'", "")
                            cleaned_value = f"mongodb://mongo:{password}@mongodb.railway.internal:27017"
            
            # 수정된 값으로 환경변수 재설정
            os.environ[var_name] = cleaned_value
            print(f"🔧 환경변수 수정: {var_name} = {cleaned_value.replace(os.getenv('MONGO_INITDB_ROOT_PASSWORD', ''), '***') if 'PASSWORD' in var_name else cleaned_value}")

def main():
    """메인 함수"""
    print("🚀 EORA AI Railway 서버 시작")
    print("=" * 50)
    
    # 환경변수 자동 수정
    print("🔧 환경변수 자동 수정 중...")
    fix_environment_variables()
    
    # final_server.py 실행
    print("🚀 final_server.py 실행 중...")
    
    # final_server 모듈 import 및 실행
    try:
        import final_server
        print("✅ final_server 모듈 로드 성공")
        
        # FastAPI 앱 실행
        import uvicorn
        uvicorn.run(
            final_server.app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8080")),
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ final_server 모듈 로드 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 