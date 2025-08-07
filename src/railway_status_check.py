#!/usr/bin/env python3
"""
Railway 배포 사이트 상태 확인 스크립트
"""

import requests
import json
from datetime import datetime

def check_railway_status():
    """Railway 배포 사이트 상태 확인"""
    base_url = "https://web-production-40c0.up.railway.app"
    
    print("🚂 Railway 배포 사이트 상태 확인")
    print("=" * 50)
    print(f"🔍 대상 URL: {base_url}")
    print(f"⏰ 확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 테스트 엔드포인트들
    endpoints = [
        ("/", "메인 페이지"),
        ("/api/status", "API 상태"),
        ("/api/health", "헬스 체크"),
        ("/chat", "채팅 페이지")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            print(f"📡 {description} 확인 중... ({endpoint})")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            status = "✅ 정상" if response.status_code == 200 else f"⚠️ 상태코드: {response.status_code}"
            print(f"   결과: {status}")
            
            results.append({
                "endpoint": endpoint,
                "description": description,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200
            })
            
        except requests.exceptions.Timeout:
            print(f"   결과: ❌ 타임아웃 (10초 초과)")
            results.append({
                "endpoint": endpoint,
                "description": description,
                "status_code": None,
                "response_time": None,
                "success": False,
                "error": "Timeout"
            })
            
        except requests.exceptions.ConnectionError:
            print(f"   결과: ❌ 연결 실패")
            results.append({
                "endpoint": endpoint,
                "description": description,
                "status_code": None,
                "response_time": None,
                "success": False,
                "error": "Connection Error"
            })
            
        except Exception as e:
            print(f"   결과: ❌ 오류: {str(e)}")
            results.append({
                "endpoint": endpoint,
                "description": description,
                "status_code": None,
                "response_time": None,
                "success": False,
                "error": str(e)
            })
    
    print()
    print("📊 상태 요약")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    print(f"✅ 정상: {success_count}/{total_count}")
    print(f"❌ 실패: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 모든 서비스가 정상 작동 중입니다!")
        print("✅ 세션 삭제 및 GPT 대화 기능을 테스트해보세요.")
    elif success_count > 0:
        print(f"\n⚠️ 일부 서비스에 문제가 있습니다. ({success_count}/{total_count} 정상)")
        print("🔄 재배포가 완료될 때까지 기다리거나 환경변수를 다시 확인하세요.")
    else:
        print("\n❌ 모든 서비스에 문제가 있습니다.")
        print("🔧 환경변수 설정 및 배포 상태를 확인하세요.")
    
    return results

def test_chat_api():
    """채팅 API 테스트"""
    print("\n🤖 GPT 채팅 API 테스트")
    print("=" * 30)
    
    try:
        url = "https://web-production-40c0.up.railway.app/api/chat"
        payload = {
            "message": "안녕하세요, 테스트 메시지입니다.",
            "session_id": "test_session"
        }
        
        print("📤 테스트 메시지 전송 중...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ GPT 대화 기능 정상 작동!")
            try:
                data = response.json()
                if "response" in data:
                    print(f"🤖 AI 응답: {data['response'][:100]}...")
                else:
                    print("⚠️ 응답 형식이 예상과 다름")
            except:
                print("⚠️ JSON 파싱 실패")
        else:
            print(f"❌ GPT 대화 실패: 상태코드 {response.status_code}")
            print(f"   오류 내용: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ GPT 대화 테스트 오류: {str(e)}")

if __name__ == "__main__":
    # 기본 상태 확인
    results = check_railway_status()
    
    # 채팅 API 테스트
    if any(r["success"] for r in results):
        test_chat_api()
    
    print("\n" + "=" * 50)
    print("💡 문제가 계속되면:")
    print("1. Railway 대시보드에서 배포 로그 확인")
    print("2. 환경변수 OPENAI_API_KEY 재확인") 
    print("3. 서비스 재배포 시도")
    print("=" * 50) 