#!/usr/bin/env python3
"""
AI 패키지 모듈 테스트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append('.')

def test_ai_modules():
    """AI 패키지의 모든 모듈을 테스트합니다."""
    print("🧠 AI 패키지 모듈 테스트 시작")
    
    try:
        # ai.prompt_modifier 테스트
        print("\n=== ai.prompt_modifier 모듈 테스트 ===")
        from ai.prompt_modifier import update_ai_prompt, get_prompt_modification_history
        
        test_prompt = "안녕하세요. 간단한 질문이 있습니다."
        modified_prompt = update_ai_prompt(test_prompt, "enhancement")
        print(f"✅ 프롬프트 수정 성공: {len(modified_prompt)} 문자")
        
        history = get_prompt_modification_history()
        print(f"✅ 수정 이력 조회 성공: {len(history)}개 항목")
        
        print("✅ ai.prompt_modifier 모듈 모든 테스트 통과!")
        
    except Exception as e:
        print(f"❌ ai.prompt_modifier 모듈 테스트 실패: {e}")
        return False
    
    try:
        # ai.ai_router 테스트
        print("\n=== ai.ai_router 모듈 테스트 ===")
        from ai.ai_router import route_ai_request, get_ai_roles
        
        result = route_ai_request("데이터를 분석해주세요")
        print(f"✅ AI 라우팅 성공: {result['role']}")
        
        roles = get_ai_roles()
        print(f"✅ AI 역할 목록 조회 성공: {len(roles)}개 역할")
        
        print("✅ ai.ai_router 모듈 모든 테스트 통과!")
        
    except Exception as e:
        print(f"❌ ai.ai_router 모듈 테스트 실패: {e}")
        return False
    
    try:
        # ai.brain_core 테스트
        print("\n=== ai.brain_core 모듈 테스트 ===")
        from ai.brain_core import think, get_brain_status
        
        thought_result = think("안녕하세요")
        print(f"✅ 사고 프로세스 성공: {thought_result['thought_id']}")
        
        brain_status = get_brain_status()
        print(f"✅ 두뇌 상태 조회 성공: 의식수준 {brain_status['consciousness_level']:.2f}")
        
        print("✅ ai.brain_core 모듈 모든 테스트 통과!")
        
    except Exception as e:
        print(f"❌ ai.brain_core 모듈 테스트 실패: {e}")
        return False
    
    try:
        # gpt_router import 테스트
        print("\n=== gpt_router import 테스트 ===")
        from gpt_router import ask, handle_prompt_update
        
        print("✅ gpt_router 모듈 import 성공")
        print("✅ ai 패키지 연동 성공")
        
    except Exception as e:
        print(f"❌ gpt_router import 테스트 실패: {e}")
        return False
    
    print("\n==================================================")
    print("📊 AI 패키지 테스트 결과 요약")
    print("==================================================")
    print("통과: 4/4")
    print("🎉 모든 AI 패키지 모듈이 성공적으로 작동합니다!")
    print("✅ ai 패키지 누락 문제가 완전히 해결되었습니다!")
    
    return True

if __name__ == "__main__":
    success = test_ai_modules()
    sys.exit(0 if success else 1) 