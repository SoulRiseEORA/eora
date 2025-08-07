#!/usr/bin/env python3
"""
Railway 서버 테스트 버전
"""

import os
import re

def fix_environment_variables():
    """환경변수 값을 자동으로 정리하고 수정"""
    print("🔧 환경변수 자동 수정 시작")
    
    # MongoDB 관련 환경변수들
    mongo_vars = [
        "MONGO_PUBLIC_URL",
        "MONGO_URL", 
        "MONGO_INITDB_ROOT_PASSWORD",
        "MONGO_INITDB_ROOT_USERNAME"
    ]
    
    for var_name in mongo_vars:
        value = os.getenv(var_name, "")
        print(f"📋 원본 {var_name}: {value}")
        
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
            print(f"✅ 수정된 {var_name}: {cleaned_value.replace(os.getenv('MONGO_INITDB_ROOT_PASSWORD', ''), '***') if 'PASSWORD' in var_name else cleaned_value}")
        else:
            print(f"⚠️ {var_name}: 설정되지 않음")

def main():
    """메인 함수"""
    print("🚀 Railway 서버 테스트")
    print("=" * 50)
    
    # 환경변수 자동 수정
    fix_environment_variables()
    
    print("\n✅ 환경변수 수정 완료!")
    print("이제 final_server.py를 실행할 수 있습니다.")

if __name__ == "__main__":
    main() 