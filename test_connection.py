#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 서버 연결 테스트
"""

import requests
import json
from datetime import datetime

def test_server_connection():
    """서버 연결 테스트"""
    base_url = "http://127.0.0.1:8002"
    
    print("🧪 EORA AI 서버 연결 테스트")
    print("=" * 50)
    
    # 테스트할 엔드포인트들
    endpoints = [
        ("/", "홈페이지"),
        ("/api/status", "API 상태"),
        ("/health", "헬스 체크"),
        ("/info", "서버 정보"),
        ("/test", "테스트 페이지")
    ]
    
    for endpoint, description in endpoints:
        try:
            url = base_url + endpoint
            print(f"\n📡 {description} 테스트: {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ 성공 (상태 코드: {response.status_code})")
                
                # JSON 응답인 경우 내용 출력
                if endpoint in ["/api/status", "/health", "/info"]:
                    try:
                        data = response.json()
                        print(f"📊 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    except:
                        print("📄 HTML 응답")
                else:
                    print("📄 HTML 응답")
                    
            else:
                print(f"❌ 실패 (상태 코드: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 연결 실패: 서버에 연결할 수 없습니다")
        except requests.exceptions.Timeout:
            print(f"❌ 타임아웃: 요청 시간이 초과되었습니다")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_server_connection() 