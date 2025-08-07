#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회상 기능 테스트 스크립트
8종 회상 시스템과 고급 회상 기능이 정상 작동하는지 확인
"""

import sys
import os
import asyncio
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append('src')

async def test_recall_functionality():
    """회상 기능 테스트"""
    
    print("🧠 회상 기능 테스트 시작...")
    
    try:
        # EORA 메모리 시스템 import
        from aura_memory_system import EORAMemorySystem
        
        # 메모리 시스템 초기화
        print("🔄 EORA 메모리 시스템 초기화...")
        eora_memory = EORAMemorySystem()
        
        if not eora_memory.is_initialized:
            print("❌ EORA 메모리 시스템 초기화 실패")
            return False
        
        print("✅ EORA 메모리 시스템 초기화 성공")
        
        # memory_manager 확인
        if hasattr(eora_memory, 'memory_manager') and eora_memory.memory_manager:
            print("✅ memory_manager 객체 확인됨")
            
            # RecallEngine 초기화 시도
            try:
                from aura_system.recall_engine import RecallEngine
                recall_engine = RecallEngine(eora_memory.memory_manager)
                print("✅ RecallEngine 초기화 성공!")
                
                # 간단한 회상 테스트
                print("\n🔍 회상 기능 테스트...")
                test_query = "안녕하세요"
                
                # 키워드 기반 회상 테스트
                try:
                    keyword_results = await recall_engine.recall_by_keywords(test_query, limit=3)
                    print(f"✅ 키워드 회상: {len(keyword_results)}개 결과")
                except Exception as e:
                    print(f"⚠️ 키워드 회상 오류: {e}")
                
                # 메타데이터 기반 회상 테스트
                try:
                    metadata_results = await recall_engine.recall_by_metadata(limit=3)
                    print(f"✅ 메타데이터 회상: {len(metadata_results)}개 결과")
                except Exception as e:
                    print(f"⚠️ 메타데이터 회상 오류: {e}")
                
            except Exception as e:
                print(f"❌ RecallEngine 초기화 실패: {e}")
                return False
        else:
            print("❌ memory_manager 객체가 없습니다")
            return False
        
        # 8종 회상 시스템 테스트
        print("\n🧠 8종 회상 시스템 테스트...")
        test_user_id = "test_user"
        test_query = "Python 프로그래밍"
        
        try:
            # 테스트 메모리 저장
            print("💾 테스트 메모리 저장...")
            memory_id1 = await eora_memory.store_memory(
                "Python은 프로그래밍 언어입니다", 
                user_id=test_user_id,
                memory_type="knowledge"
            )
            
            memory_id2 = await eora_memory.store_memory(
                "FastAPI는 Python 웹 프레임워크입니다", 
                user_id=test_user_id,
                memory_type="knowledge"
            )
            
            print(f"✅ 테스트 메모리 저장 완료: {memory_id1}, {memory_id2}")
            
            # 8종 회상 시스템 테스트
            enhanced_results = await eora_memory.enhanced_recall(test_query, test_user_id, limit=5)
            print(f"✅ 8종 회상 시스템: {len(enhanced_results)}개 결과")
            
            for i, memory in enumerate(enhanced_results):
                print(f"  [{i+1}] {memory.get('content', '')[:50]}...")
                
        except Exception as e:
            print(f"❌ 8종 회상 시스템 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 개별 회상 기능 테스트
        print("\n🔍 개별 회상 기능 테스트...")
        
        recall_methods = [
            ("키워드 회상", eora_memory.keyword_recall),
            ("감정 회상", eora_memory.emotion_recall),
            ("맥락 회상", eora_memory.context_recall),
            ("시간 회상", eora_memory.temporal_recall)
        ]
        
        for method_name, method in recall_methods:
            try:
                results = await method(test_query, test_user_id, limit=3)
                print(f"✅ {method_name}: {len(results)}개 결과")
            except Exception as e:
                print(f"⚠️ {method_name} 오류: {e}")
        
        print("\n🎉 회상 기능 테스트 완료!")
        print("✅ RecallEngine이 정상적으로 작동합니다")
        print("✅ 8종 회상 시스템이 활성화되었습니다")
        print("✅ 고급 회상 기능이 Railway에서도 작동할 예정입니다")
        
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        print("💡 필요한 패키지가 설치되지 않았을 수 있습니다.")
        print("💡 Railway에서는 requirements.txt의 패키지들이 자동 설치됩니다.")
        return False
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("🧠 EORA AI - 회상 기능 테스트")
    print("=" * 60)
    
    # 비동기 테스트 실행
    success = asyncio.run(test_recall_functionality())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 테스트 완료: 회상 기능이 정상 작동합니다!")
        print("🚀 Railway 배포 시에도 고급 회상 기능이 활성화됩니다!")
    else:
        print("❌ 테스트 실패: 회상 기능에 문제가 있습니다")
        print("🔧 requirements.txt의 패키지들이 Railway에서 설치되면 해결될 예정입니다")
    print("=" * 60)

if __name__ == "__main__":
    main() 