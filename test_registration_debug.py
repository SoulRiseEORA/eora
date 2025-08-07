#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회원가입 문제 디버깅 스크립트
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_registration():
    """회원가입 테스트"""
    
    # 테스트 데이터
    test_user = {
        "email": f"debug_test_{int(datetime.now().timestamp())}@example.com",
        "password": "test123456",
        "confirm_password": "test123456", 
        "name": "디버그테스트"
    }
    
    print("🧪 회원가입 디버깅 테스트 시작")
    print(f"📧 테스트 이메일: {test_user['email']}")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # 회원가입 요청
            async with session.post(
                "http://localhost:8000/api/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📊 응답 상태코드: {response.status}")
                print(f"📊 응답 헤더: {dict(response.headers)}")
                
                # 응답 내용 확인
                try:
                    response_data = await response.json()
                    print(f"📊 응답 데이터: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                except:
                    # JSON이 아닌 경우 텍스트로 읽기
                    response_text = await response.text()
                    print(f"📊 응답 텍스트: {response_text}")
                
                if response.status == 200:
                    print("✅ 회원가입 성공!")
                else:
                    print(f"❌ 회원가입 실패 - 상태코드: {response.status}")
                    
        except Exception as e:
            print(f"❌ 요청 오류: {e}")
            print(f"❌ 오류 타입: {type(e)}")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_registration())