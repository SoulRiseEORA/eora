#!/usr/bin/env python3
"""
Railway 배포 상태 및 MongoDB 연결 확인
"""

import os
import requests
import time

def check_railway_deployment():
    """Railway 배포 상태 확인"""
    
    print("🚂 Railway 배포 상태 확인")
    print("=" * 50)
    
    # Railway URL (실제 배포된 URL로 변경 필요)
    railway_urls = [
        "https://www.eora.life",
        "https://eora.life",
        "https://eora-ai.railway.app"
    ]
    
    for url in railway_urls:
        print(f"\n🔍 {url} 확인 중...")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ 배포 성공: {url}")
                print(f"   상태 코드: {response.status_code}")
                print(f"   응답 시간: {response.elapsed.total_seconds():.2f}초")
                return url
            else:
                print(f"❌ 배포 실패: {url}")
                print(f"   상태 코드: {response.status_code}")
        except Exception as e:
            print(f"❌ 연결 실패: {url}")
            print(f"   오류: {str(e)}")
    
    return None

def check_railway_env_vars():
    """Railway 환경변수 확인"""
    
    print("\n🔍 Railway 환경변수 확인")
    print("=" * 30)
    
    # Railway MongoDB 관련 환경변수
    env_vars = [
        "MONGO_INITDB_ROOT_PASSWORD",
        "MONGO_INITDB_ROOT_USERNAME", 
        "MONGO_PUBLIC_URL",
        "MONGO_URL",
        "RAILWAY_TCP_PROXY_DOMAIN",
        "RAILWAY_TCP_PROXY_PORT",
        "RAILWAY_PRIVATE_DOMAIN",
        "PORT",
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_PROJECT_ID"
    ]
    
    found_vars = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            found_vars.append(var)
            # 비밀번호는 마스킹 처리
            if "PASSWORD" in var:
                masked_value = value[:3] + "*" * (len(value) - 6) + value[-3:] if len(value) > 6 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: (설정되지 않음)")
    
    return found_vars

def test_mongo_connection():
    """MongoDB 연결 테스트"""
    
    print("\n🔗 MongoDB 연결 테스트")
    print("=" * 30)
    
    try:
        from pymongo import MongoClient
        print("✅ PyMongo 라이브러리 로드 성공")
    except ImportError:
        print("❌ PyMongo 라이브러리가 설치되지 않았습니다.")
        return False
    
    # Railway 환경변수에서 MongoDB 설정 읽기
    mongo_root_user = os.getenv("MONGO_INITDB_ROOT_USERNAME", "mongo")
    mongo_root_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "HYxotmUHxMxbYAejsOxEnHwrgKpAochC")
    
    # 연결 URL 우선순위
    connection_urls = []
    
    # 1. MONGO_PUBLIC_URL (가장 우선)
    mongo_public_url = os.getenv("MONGO_PUBLIC_URL")
    if mongo_public_url:
        connection_urls.append(("MONGO_PUBLIC_URL", mongo_public_url))
    
    # 2. MONGO_URL
    mongo_url = os.getenv("MONGO_URL")
    if mongo_url:
        connection_urls.append(("MONGO_URL", mongo_url))
    
    # 3. Railway 환경변수로 구성
    railway_tcp_proxy_domain = os.getenv("RAILWAY_TCP_PROXY_DOMAIN")
    railway_tcp_proxy_port = os.getenv("RAILWAY_TCP_PROXY_PORT")
    railway_private_domain = os.getenv("RAILWAY_PRIVATE_DOMAIN")
    
    if railway_tcp_proxy_domain and railway_tcp_proxy_port:
        public_url = f"mongodb://{mongo_root_user}:{mongo_root_password}@{railway_tcp_proxy_domain}:{railway_tcp_proxy_port}"
        connection_urls.append(("Railway 공개 URL (자동 구성)", public_url))
    
    if railway_private_domain:
        private_url = f"mongodb://{mongo_root_user}:{mongo_root_password}@{railway_private_domain}:27017"
        connection_urls.append(("Railway 내부 URL (자동 구성)", private_url))
    
    # 4. 기본값
    default_url = f"mongodb://{mongo_root_user}:{mongo_root_password}@localhost:27017"
    connection_urls.append(("기본 URL", default_url))
    
    # 각 URL로 연결 시도
    for i, (name, url) in enumerate(connection_urls, 1):
        print(f"\n{i}. {name} 테스트:")
        print(f"   URL: {url.replace(mongo_root_password, '***')}")
        
        try:
            client = MongoClient(url, serverSelectionTimeoutMS=10000)
            client.admin.command('ping')
            print(f"   ✅ 연결 성공!")
            
            # 데이터베이스 및 컬렉션 테스트
            db = client.eora_ai
            users_collection = db.users
            
            # 컬렉션 목록 확인
            collections = db.list_collection_names()
            print(f"   📋 현재 컬렉션 목록: {collections}")
            
            # 테스트 문서 삽입
            test_user = {
                "user_id": "test_user_123",
                "email": "test@example.com",
                "name": "테스트 사용자",
                "created_at": "2024-01-01T00:00:00"
            }
            
            result = users_collection.insert_one(test_user)
            print(f"   ✅ 테스트 사용자 생성 성공: {result.inserted_id}")
            
            # 테스트 문서 삭제
            users_collection.delete_one({"user_id": "test_user_123"})
            print(f"   ✅ 테스트 사용자 삭제 완료")
            
            client.close()
            return True, name, url
            
        except Exception as e:
            print(f"   ❌ 연결 실패: {type(e).__name__}")
            if "Authentication failed" in str(e):
                print(f"   🔍 인증 실패 - 사용자명/비밀번호 확인 필요")
            elif "getaddrinfo failed" in str(e):
                print(f"   🔍 호스트 주소를 찾을 수 없음 - 네트워크 연결 확인 필요")
            elif "timeout" in str(e).lower():
                print(f"   🔍 연결 시간 초과 - 서비스 상태 확인 필요")
    
    return False, None, None

def main():
    """메인 함수"""
    print("🚀 Railway 배포 상태 및 MongoDB 연결 확인")
    print("=" * 60)
    
    # 1. Railway 배포 상태 확인
    deployed_url = check_railway_deployment()
    
    # 2. Railway 환경변수 확인
    found_vars = check_railway_env_vars()
    
    # 3. MongoDB 연결 테스트
    success, connection_name, connection_url = test_mongo_connection()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 결과 요약")
    print("=" * 60)
    
    if deployed_url:
        print(f"✅ Railway 배포: 성공 ({deployed_url})")
    else:
        print("❌ Railway 배포: 실패 또는 확인 불가")
    
    if found_vars:
        print(f"✅ Railway 환경변수: {len(found_vars)}개 설정됨")
    else:
        print("❌ Railway 환경변수: 설정되지 않음")
    
    if success:
        print(f"✅ MongoDB 연결: 성공 ({connection_name})")
        print(f"   연결 URL: {connection_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
    else:
        print("❌ MongoDB 연결: 실패")
    
    # 권장사항
    print("\n💡 권장사항:")
    if not deployed_url:
        print("1. Railway 프로젝트가 배포되었는지 확인하세요")
        print("2. GitHub 저장소가 Railway와 연결되었는지 확인하세요")
    
    if not found_vars:
        print("3. Railway 대시보드에서 환경변수가 설정되었는지 확인하세요")
    
    if not success:
        print("4. Railway MongoDB 서비스가 실행 중인지 확인하세요")
        print("5. Railway 대시보드에서 MongoDB 연결 정보를 확인하세요")

if __name__ == "__main__":
    main() 