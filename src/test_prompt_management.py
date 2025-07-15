#!/usr/bin/env python3
"""
프롬프트 관리 기능 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_prompt_management():
    """프롬프트 관리 기능 테스트"""
    print("📝 프롬프트 관리 기능 테스트 시작...")
    
    # 세션 생성
    session = requests.Session()
    
    # 1. 로그인
    print("\n1️⃣ 관리자 로그인 시도...")
    login_data = {
        "email": "admin@eora.com",
        "password": "admin123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"로그인 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 로그인 성공: {data.get('message', '')}")
            print(f"관리자 권한: {data.get('data', {}).get('is_admin', False)}")
        else:
            print(f"❌ 로그인 실패: {response.text}")
            return False
    except Exception as e:
        print(f"로그인 오류: {e}")
        return False
    
    # 2. 프롬프트 목록 조회
    print("\n2️⃣ 프롬프트 목록 조회...")
    try:
        response = session.get(f"{BASE_URL}/api/prompts")
        print(f"프롬프트 조회 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ 프롬프트 조회 성공: {len(prompts)}개 프롬프트")
            
            # AI별 프롬프트 개수 출력
            ai_counts = {}
            for prompt in prompts:
                ai_name = prompt.get('ai_name', 'unknown')
                ai_counts[ai_name] = ai_counts.get(ai_name, 0) + 1
            
            print("AI별 프롬프트 개수:")
            for ai_name, count in ai_counts.items():
                print(f"  - {ai_name}: {count}개")
            
            # AI1의 system 프롬프트 확인
            ai1_system = [p for p in prompts if p.get('ai_name') == 'ai1' and p.get('category') == 'system']
            if ai1_system:
                print(f"\n✅ AI1 system 프롬프트 확인: {len(ai1_system)}개")
                print(f"   내용 길이: {len(ai1_system[0].get('content', ''))}자")
            else:
                print("❌ AI1 system 프롬프트를 찾을 수 없습니다.")
                
        else:
            print(f"❌ 프롬프트 조회 실패: {response.text}")
            return False
    except Exception as e:
        print(f"프롬프트 조회 오류: {e}")
        return False
    
    # 3. 새 프롬프트 추가 테스트
    print("\n3️⃣ 새 프롬프트 추가 테스트...")
    new_prompt = {
        "name": "테스트 프롬프트",
        "category": "guide",
        "content": "이것은 테스트용 프롬프트입니다.",
        "description": "테스트를 위한 임시 프롬프트",
        "tags": ["test", "guide"],
        "ai_name": "ai1"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/prompts", json=new_prompt)
        print(f"프롬프트 추가 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 프롬프트 추가 성공: {data.get('message', '')}")
            added_prompt_id = data.get('prompt', {}).get('id')
            print(f"   추가된 프롬프트 ID: {added_prompt_id}")
        else:
            print(f"❌ 프롬프트 추가 실패: {response.text}")
            return False
    except Exception as e:
        print(f"프롬프트 추가 오류: {e}")
        return False
    
    # 4. 프롬프트 수정 테스트
    if added_prompt_id:
        print(f"\n4️⃣ 프롬프트 수정 테스트 (ID: {added_prompt_id})...")
        updated_prompt = {
            "name": "수정된 테스트 프롬프트",
            "category": "guide",
            "content": "이것은 수정된 테스트용 프롬프트입니다.",
            "description": "수정된 테스트를 위한 임시 프롬프트",
            "tags": ["test", "guide", "updated"],
            "ai_name": "ai1"
        }
        
        try:
            response = session.put(f"{BASE_URL}/api/prompts/{added_prompt_id}", json=updated_prompt)
            print(f"프롬프트 수정 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 프롬프트 수정 성공: {data.get('message', '')}")
            else:
                print(f"❌ 프롬프트 수정 실패: {response.text}")
        except Exception as e:
            print(f"프롬프트 수정 오류: {e}")
    
    # 5. 프롬프트 삭제 테스트
    if added_prompt_id:
        print(f"\n5️⃣ 프롬프트 삭제 테스트 (ID: {added_prompt_id})...")
        try:
            response = session.delete(f"{BASE_URL}/api/prompts/{added_prompt_id}")
            print(f"프롬프트 삭제 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 프롬프트 삭제 성공: {data.get('message', '')}")
            else:
                print(f"❌ 프롬프트 삭제 실패: {response.text}")
        except Exception as e:
            print(f"프롬프트 삭제 오류: {e}")
    
    print("\n🎉 프롬프트 관리 기능 테스트 완료!")
    return True

if __name__ == "__main__":
    test_prompt_management() 