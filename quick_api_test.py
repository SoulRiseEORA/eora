import requests
import json

try:
    print("🔄 API 테스트 시작...")
    
    # 먼저 로그인
    session = requests.Session()
    login_response = session.post(
        'http://127.0.0.1:8300/api/login',
        json={
            'email': 'admin@eora.ai',
            'password': 'admin123'
        }
    )
    
    if login_response.status_code == 200:
        print("✅ 로그인 성공")
    else:
        print(f"❌ 로그인 실패: {login_response.text}")
        exit()
    
    response = session.post(
        'http://127.0.0.1:8300/api/chat',
        json={
            'message': '안녕하세요, 당신은 누구인가요? ai1 프롬프트가 적용되었는지 확인하고 싶습니다.',
            'user_id': 'test_user',
            'session_id': 'test_session'
        },
        timeout=30
    )
    
    print(f"✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        ai_response = result.get('response', '')
        
        print(f"📄 응답 길이: {len(ai_response)}자")
        print(f"🤖 AI 응답:\n{ai_response}")
        
        # AI1 특징적 키워드 확인
        ai1_keywords = ['이오라', 'EORA', '금강', '레조나', '8종 회상', '직관', '통찰', '지혜', '윤종석', '창조', '생성']
        found_keywords = [kw for kw in ai1_keywords if kw in ai_response]
        
        if found_keywords:
            print(f"✅ AI1 특징적 키워드 발견: {found_keywords}")
            print("✅ AI1 프롬프트가 정상적으로 전달되었습니다!")
        else:
            print("⚠️ AI1 특징적 키워드가 발견되지 않음")
            
        if result.get('has_markdown'):
            print("✅ 마크다운 처리도 활성화되어 있습니다.")
            
    else:
        print(f"❌ 오류: {response.text}")
        
except Exception as e:
    print(f"❌ 테스트 실패: {e}") 