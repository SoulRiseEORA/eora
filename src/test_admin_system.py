#!/usr/bin/env python3
"""
관리자 시스템 전용 테스트 스크립트
"""

import requests
import json
import time

def test_admin_system():
    """관리자 시스템 테스트"""
    print("=== 관리자 시스템 전용 테스트 ===")
    
    # 서버 URL
    base_url = "http://127.0.0.1:8001"
    
    # 1. 관리자 통계 테스트
    print("\n--- 1. 관리자 통계 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 관리자 통계: {data}")
        else:
            print(f"❌ 관리자 통계 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 관리자 통계 오류: {e}")
    
    # 2. 사용자 목록 테스트
    print(f"\n--- 2. 사용자 목록 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 사용자 목록: {len(data.get('users', []))}명")
            for user in data.get('users', [])[:3]:  # 처음 3명만 표시
                print(f"  - {user.get('user_id')}: {user.get('points', 0)}포인트")
        else:
            print(f"❌ 사용자 목록 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 사용자 목록 오류: {e}")
    
    # 3. 포인트 통계 테스트
    print(f"\n--- 3. 포인트 통계 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/points/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"✅ 포인트 통계:")
            print(f"  - 총 판매 포인트: {stats.get('total_sold', 0):,}")
            print(f"  - 총 사용 포인트: {stats.get('total_used', 0):,}")
            print(f"  - 잔여 포인트: {stats.get('remaining', 0):,}")
        else:
            print(f"❌ 포인트 통계 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 포인트 통계 오류: {e}")
    
    # 4. 포인트 사용자 목록 테스트
    print(f"\n--- 4. 포인트 사용자 목록 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/points/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 포인트 사용자: {len(data.get('users', []))}명")
            for user in data.get('users', [])[:3]:  # 처음 3명만 표시
                print(f"  - {user.get('user_id')}: {user.get('current_points', 0)}포인트 (총 사용: {user.get('total_used', 0)})")
        else:
            print(f"❌ 포인트 사용자 목록 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 포인트 사용자 목록 오류: {e}")
    
    # 5. 포인트 조정 테스트
    print(f"\n--- 5. 포인트 조정 테스트 ---")
    try:
        # test_user에게 1000포인트 추가
        response = requests.post(
            f"{base_url}/api/admin/points/adjust",
            json={
                "user_id": "test_user",
                "amount": 1000,
                "action": "add"
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 포인트 조정: {data}")
        else:
            print(f"❌ 포인트 조정 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 포인트 조정 오류: {e}")
    
    # 6. 저장소 통계 테스트
    print(f"\n--- 6. 저장소 통계 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/storage")
        if response.status_code == 200:
            data = response.json()
            storage = data.get('storage', {})
            print(f"✅ 저장소 통계:")
            print(f"  - 데이터베이스 크기: {storage.get('db_size', 0)} MB")
            print(f"  - 파일 저장소: {storage.get('file_size', 0)} MB")
            print(f"  - 백업 크기: {storage.get('backup_size', 0)} MB")
        else:
            print(f"❌ 저장소 통계 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 저장소 통계 오류: {e}")
    
    # 7. 시스템 모니터링 테스트
    print(f"\n--- 7. 시스템 모니터링 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/monitoring")
        if response.status_code == 200:
            data = response.json()
            monitoring = data.get('monitoring', {})
            print(f"✅ 시스템 모니터링:")
            print(f"  - 동시 접속자: {monitoring.get('concurrent_users', 0)}명")
            print(f"  - API 호출 수: {monitoring.get('api_calls', 0)}회")
            print(f"  - 평균 응답시간: {monitoring.get('avg_response_time', 0)}ms")
        else:
            print(f"❌ 시스템 모니터링 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 시스템 모니터링 오류: {e}")
    
    # 8. 자원 통계 테스트
    print(f"\n--- 8. 자원 통계 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/resources")
        if response.status_code == 200:
            data = response.json()
            resources = data.get('resources', {})
            print(f"✅ 자원 통계:")
            print(f"  - CPU 사용률: {resources.get('cpu_usage', 0)}%")
            print(f"  - 메모리 사용률: {resources.get('memory_usage', 0)}%")
            print(f"  - 디스크 사용률: {resources.get('disk_usage', 0)}%")
            print(f"  - 업로드 속도: {resources.get('upload_speed', 0)} KB/s")
            print(f"  - 다운로드 속도: {resources.get('download_speed', 0)} KB/s")
        else:
            print(f"❌ 자원 통계 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 자원 통계 오류: {e}")
    
    # 9. 프롬프트 관리 테스트
    print(f"\n--- 9. 프롬프트 관리 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/admin/prompts/ai1/system")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                prompt = data.get('prompt', '')
                print(f"✅ 프롬프트 조회 성공 (길이: {len(prompt)} 문자)")
            else:
                print(f"❌ 프롬프트 조회 실패: {data.get('error')}")
        else:
            print(f"❌ 프롬프트 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 프롬프트 조회 오류: {e}")
    
    # 10. 백업 생성 테스트
    print(f"\n--- 10. 백업 생성 테스트 ---")
    try:
        response = requests.post(f"{base_url}/api/admin/backup")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 백업 생성: {data}")
        else:
            print(f"❌ 백업 생성 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 백업 생성 오류: {e}")
    
    print(f"\n=== 관리자 시스템 테스트 완료 ===")

if __name__ == "__main__":
    test_admin_system() 