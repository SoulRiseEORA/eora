#!/usr/bin/env python3
"""
test_utils.py
utils_lightweight 모듈과 recall_engine_v3 모듈 테스트
"""

import sys
import os
sys.path.append('.')

def test_utils_lightweight():
    """utils_lightweight 모듈 테스트"""
    print("=== utils_lightweight 모듈 테스트 ===")
    try:
        from utils_lightweight import simple_embed, cosine_similarity, simple_emotion
        
        # 테스트 텍스트
        test_text = "나는 오늘 정말 기쁘고 행복하다"
        
        # 임베딩 테스트
        embedding = simple_embed(test_text)
        print(f"✅ 임베딩 생성 성공: {len(embedding)}차원")
        
        # 감정 분석 테스트
        emotion = simple_emotion(test_text)
        print(f"✅ 감정 분석 성공: {emotion}")
        
        # 유사도 테스트
        text2 = "오늘은 슬프고 우울하다"
        emb2 = simple_embed(text2)
        similarity = cosine_similarity(embedding, emb2)
        print(f"✅ 유사도 계산 성공: {similarity:.3f}")
        
        print("✅ utils_lightweight 모듈 모든 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ utils_lightweight 테스트 실패: {str(e)}")
        return False

def test_recall_engine():
    """recall_engine_v3 모듈 테스트"""
    print("\n=== recall_engine_v3 모듈 테스트 ===")
    try:
        from eora_modular.recall_engine_v3 import RecallEngineV3
        
        # 엔진 생성
        engine = RecallEngineV3()
        print("✅ RecallEngineV3 생성 성공")
        
        # 메모리 저장 테스트
        mem_id = engine.store_memory(
            "나는 실패할까 두려워", 
            "실패는 성장의 일부입니다.", 
            "fear", 
            ["실패", "두려움"]
        )
        print(f"✅ 메모리 저장 성공: ID {mem_id}")
        
        # 메모리 회상 테스트
        recalls = engine.recall_memories("실패 두려움")
        print(f"✅ 메모리 회상 성공: {len(recalls)}개 결과")
        
        # 감정 기반 회상 테스트
        emotion_recalls = engine.recall_by_emotion("fear")
        print(f"✅ 감정 기반 회상 성공: {len(emotion_recalls)}개 결과")
        
        print("✅ recall_engine_v3 모듈 모든 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ recall_engine_v3 테스트 실패: {str(e)}")
        return False

def test_memory_chain():
    """memory_chain_v4 모듈 테스트"""
    print("\n=== memory_chain_v4 모듈 테스트 ===")
    try:
        from eora_modular.memory_chain_v4 import store_memory, recall_memories
        
        # 메모리 저장 테스트
        mem_id = store_memory(
            "오늘은 의미를 찾고 싶어요.", 
            "삶의 의미에 대해 생각해볼 수 있어요.", 
            "curious", 
            ["의미", "삶"]
        )
        print(f"✅ 메모리 체인 저장 성공: ID {mem_id}")
        
        # 메모리 회상 테스트
        recalls = recall_memories("의미 삶")
        print(f"✅ 메모리 체인 회상 성공: {len(recalls)}개 결과")
        
        print("✅ memory_chain_v4 모듈 모든 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ memory_chain_v4 테스트 실패: {str(e)}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧠 EORA 시스템 모듈 테스트 시작\n")
    
    results = []
    
    # 각 모듈 테스트
    results.append(test_utils_lightweight())
    results.append(test_recall_engine())
    results.append(test_memory_chain())
    
    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"통과: {passed}/{total}")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 통과했습니다!")
        print("✅ utils_lightweight 모듈 누락 문제가 해결되었습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        print("❌ 추가 수정이 필요할 수 있습니다.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 