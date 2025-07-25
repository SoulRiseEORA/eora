"""
세션 저장 및 불러오기 시스템 수정
"""
import os
import json
import shutil
from datetime import datetime

def main():
    print("🔍 세션 시스템 진단 및 수정 중...")
    
    # 1. 세션 저장 디렉토리 확인
    session_dir = "sessions_backup"
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        print(f"✅ 세션 디렉토리 생성: {session_dir}")
    else:
        session_count = len([f for f in os.listdir(session_dir) if f.endswith('.json')])
        print(f"✅ 세션 디렉토리 존재: {session_dir} ({session_count}개 세션 파일)")
    
    # 2. app.py 파일에 세션 API 확인 및 수정
    app_path = "src/app.py"
    app_backup_path = "src/app_backup_before_session_fix.py"
    
    # 백업 생성
    if os.path.exists(app_path) and not os.path.exists(app_backup_path):
        shutil.copy2(app_path, app_backup_path)
        print(f"✅ app.py 백업 생성: {app_backup_path}")
    
    # API 확인
    api_found = False
    if os.path.exists(app_path):
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '@app.get("/api/sessions")' in content:
                api_found = True
                print("✅ 세션 API 엔드포인트 확인됨")
            else:
                print("❌ 세션 API 엔드포인트 없음")
    
    # 3. 테스트용 세션 파일 생성
    test_session_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    test_user_id = "test_user"
    test_file_path = os.path.join(session_dir, f"{test_user_id}_{test_session_id}.json")
    
    test_data = [
        {
            "user_message": "안녕하세요, 테스트 메시지입니다.",
            "ai_response": "안녕하세요! 테스트 응답입니다.",
            "timestamp": datetime.now().isoformat(),
            "memory_type": "conversation",
            "importance": 0.7
        },
        {
            "user_message": "세션 저장이 되나요?",
            "ai_response": "네, 정상적으로 저장되고 있습니다!",
            "timestamp": datetime.now().isoformat(),
            "memory_type": "conversation",
            "importance": 0.7
        }
    ]
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 테스트 세션 파일 생성: {test_file_path}")
    
    # 4. 세션 API 추가 (이미 있으면 스킵)
    if not api_found:
        print("⚠️ 세션 API가 없습니다. app.py 수정이 필요합니다.")
        # API 추가 로직은 복잡하므로 여기서는 생략
    
    # 5. templates/chat.html 확인
    chat_html_path = "src/templates/chat.html"
    if os.path.exists(chat_html_path):
        with open(chat_html_path, 'r', encoding='utf-8') as f:
            chat_content = f.read()
            if 'fetch(\'/api/sessions\')' in chat_content or "$.get('/api/sessions'" in chat_content:
                print("✅ chat.html에서 세션 API 호출 확인됨")
            else:
                print("❌ chat.html에서 세션 API 호출 코드가 없습니다.")
    
    # 6. 테스트 웹 페이지 생성/확인
    test_web_path = "src/templates/test_web_session.html"
    if os.path.exists(test_web_path):
        print(f"✅ 테스트 페이지 존재: {test_web_path}")
        print(f"   브라우저에서 확인: http://localhost:8001/test_web_session")
    else:
        print(f"❌ 테스트 페이지가 없습니다: {test_web_path}")
    
    print("\n🔧 진단 완료!")
    print("💡 세션 시스템 테스트 방법:")
    print("1. restart_server.bat 실행 (서버 완전 재시작)")
    print("2. 브라우저에서 http://localhost:8001/test_web_session 접속")
    print("3. 테스트 페이지에서 API 작동 확인")
    print("\n⚠️ 문제가 지속되면 개발자 도구(F12)를 열고 콘솔 오류를 확인하세요.")

if __name__ == "__main__":
    main() 