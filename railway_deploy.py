#!/usr/bin/env python3
"""
EORA AI Railway 배포 전용 서버
환경변수 자동 수정 및 안정적인 서버 실행
"""

import os
import sys
import re
import uvicorn
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def fix_environment_variables():
    """환경변수 값을 자동으로 정리하고 수정"""
    print("🔧 Railway 환경변수 자동 수정 시작")
    
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
            print(f"✅ {var_name} 수정 완료")
    
    print("🔧 환경변수 수정 완료")

def main():
    """메인 함수"""
    print("🚀 EORA AI Railway 배포 서버 시작")
    print("=" * 60)
    
    # 환경변수 자동 수정
    fix_environment_variables()
    
    # final_server 모듈 import
    try:
        import final_server
        print("✅ final_server 모듈 로드 성공")
        
        # Railway 환경 설정
        port = int(os.getenv("PORT", "8080"))
        host = "0.0.0.0"  # Railway에서는 0.0.0.0 사용
        
        print(f"📍 서버 주소: http://0.0.0.0:{port}")
        print(f"🔧 Railway 환경에서 실행 중...")
        
        # FastAPI 앱 실행
        uvicorn.run(
            final_server.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False  # Railway에서는 reload 비활성화
        )
        
    except ImportError as e:
        print(f"❌ final_server 모듈 로드 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 