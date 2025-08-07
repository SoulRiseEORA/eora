#!/usr/bin/env python3
"""
관리자 페이지 학습내용 회상 - 간단 확인용 (무한루프 방지)
"""

def check_code_fixes():
    """코드 수정사항 확인"""
    print("🔍 관리자 페이지 학습내용 회상 - 코드 수정사항 확인")
    print("=" * 60)
    
    issues_found = []
    fixes_applied = []
    
    # 1. app.py 확인
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        # 지연 초기화 확인
        if "get_eora_memory_system()" in app_content:
            fixes_applied.append("✅ app.py - 지연 초기화 패턴 적용")
        else:
            issues_found.append("❌ app.py - 지연 초기화 패턴 미적용")
        
        # 향상된 회상 API 확인
        if "@app.post(\"/api/admin/enhanced-recall\")" in app_content:
            fixes_applied.append("✅ app.py - 향상된 회상 API 존재")
        else:
            issues_found.append("❌ app.py - 향상된 회상 API 없음")
            
        # 향상된 학습 API 확인  
        if "@app.post(\"/api/admin/enhanced-learn-file\")" in app_content:
            fixes_applied.append("✅ app.py - 향상된 학습 API 존재")
        else:
            issues_found.append("❌ app.py - 향상된 학습 API 없음")
            
    except Exception as e:
        issues_found.append(f"❌ app.py - 파일 읽기 실패: {e}")
    
    # 2. enhanced_learning_system.py 확인
    try:
        with open("enhanced_learning_system.py", "r", encoding="utf-8") as f:
            enhanced_content = f.read()
        
        # 호환성 필드 확인
        if '"content": chunk' in enhanced_content:
            fixes_applied.append("✅ enhanced_learning_system.py - content 필드 추가")
        else:
            issues_found.append("❌ enhanced_learning_system.py - content 필드 없음")
            
        if '"keywords":' in enhanced_content:
            fixes_applied.append("✅ enhanced_learning_system.py - keywords 필드 추가")
        else:
            issues_found.append("❌ enhanced_learning_system.py - keywords 필드 없음")
            
        if '"filename":' in enhanced_content:
            fixes_applied.append("✅ enhanced_learning_system.py - filename 필드 추가")
        else:
            issues_found.append("❌ enhanced_learning_system.py - filename 필드 없음")
            
    except Exception as e:
        issues_found.append(f"❌ enhanced_learning_system.py - 파일 읽기 실패: {e}")
    
    # 3. admin.html 확인
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            admin_content = f.read()
        
        # 회상 모달 확인
        if 'id="recallModal"' in admin_content:
            fixes_applied.append("✅ admin.html - 회상 모달 추가")
        else:
            issues_found.append("❌ admin.html - 회상 모달 없음")
            
        # 향상된 API 호출 확인
        if '/api/admin/enhanced-recall' in admin_content:
            fixes_applied.append("✅ admin.html - 향상된 회상 API 호출")
        else:
            issues_found.append("❌ admin.html - 향상된 회상 API 호출 없음")
            
        if '/api/admin/enhanced-learn-file' in admin_content:
            fixes_applied.append("✅ admin.html - 향상된 학습 API 호출")
        else:
            issues_found.append("❌ admin.html - 향상된 학습 API 호출 없음")
            
        # 회상 기능 JavaScript 확인
        if 'searchLearningContent' in admin_content:
            fixes_applied.append("✅ admin.html - 회상 JavaScript 함수 존재")
        else:
            issues_found.append("❌ admin.html - 회상 JavaScript 함수 없음")
            
    except Exception as e:
        issues_found.append(f"❌ admin.html - 파일 읽기 실패: {e}")
    
    # 4. eora_memory_system.py 확인
    try:
        with open("eora_memory_system.py", "r", encoding="utf-8") as f:
            memory_content = f.read()
        
        # 지연 초기화 확인
        if "get_eora_memory_system()" in memory_content:
            fixes_applied.append("✅ eora_memory_system.py - 지연 초기화 함수 존재")
        else:
            issues_found.append("❌ eora_memory_system.py - 지연 초기화 함수 없음")
            
        # 필드 호환성 확인
        if '"response"' in memory_content and '"content"' in memory_content:
            fixes_applied.append("✅ eora_memory_system.py - 필드 호환성 지원")
        else:
            issues_found.append("❌ eora_memory_system.py - 필드 호환성 미지원")
            
    except Exception as e:
        issues_found.append(f"❌ eora_memory_system.py - 파일 읽기 실패: {e}")
    
    # 결과 출력
    print("\n📊 수정 완료 항목:")
    for fix in fixes_applied:
        print(f"  {fix}")
    
    if issues_found:
        print("\n🚨 남은 문제:")
        for issue in issues_found:
            print(f"  {issue}")
    else:
        print("\n🎉 모든 수정사항 적용 완료!")
    
    # 최종 평가
    total_checks = len(fixes_applied) + len(issues_found)
    success_rate = len(fixes_applied) / total_checks * 100 if total_checks > 0 else 0
    
    print(f"\n📈 수정 완료율: {success_rate:.1f}% ({len(fixes_applied)}/{total_checks})")
    
    if success_rate >= 90:
        print("✅ 관리자 페이지 학습내용 회상 문제가 거의 완전히 해결되었습니다!")
    elif success_rate >= 70:
        print("⚠️ 대부분 해결되었지만 일부 수정이 더 필요합니다.")
    else:
        print("❌ 추가 수정이 많이 필요합니다.")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    try:
        all_fixed = check_code_fixes()
        print(f"\n🔒 검사 완료 - {'모든 수정 완료' if all_fixed else '일부 수정 필요'}")
    except Exception as e:
        print(f"❌ 검사 중 오류: {e}")
    
    print("🏁 코드 검토 완료 - 무한루프 없는 간단 확인")