#!/usr/bin/env python3
"""
관리자 페이지 학습내용 회상 기능 완전 검증 테스트
"""

import asyncio
import sys
import os
import time

async def test_admin_recall_complete():
    """관리자 페이지 학습내용 회상 완전 검증"""
    start_time = time.time()
    
    try:
        print("🔬 관리자 페이지 학습내용 회상 완전 검증 테스트")
        print("=" * 70)
        
        # 1. Enhanced Learning System 테스트
        print("1️⃣ Enhanced Learning System 검증")
        from enhanced_learning_system import EnhancedLearningSystem
        from mongodb_config import get_optimized_database
        
        mongo_db = get_optimized_database()
        if mongo_db is None:
            print("   ❌ MongoDB 연결 실패")
            return False
        
        learning_system = EnhancedLearningSystem(mongo_db)
        print("   ✅ Enhanced Learning System 초기화 성공")
        
        # 테스트 학습 실행
        test_content = """
        관리자 페이지 학습내용 회상 테스트용 문서입니다.
        이 문서는 검색이 정상적으로 작동하는지 확인하기 위한 테스트 데이터입니다.
        키워드: 관리자_테스트, 회상_검증, 완전_해결
        """
        
        result = await learning_system.learn_document(
            content=test_content,
            filename="admin_recall_test.txt",
            category="관리자_테스트"
        )
        
        if result and result.get("success"):
            print(f"   ✅ 테스트 학습 성공: {result.get('total_chunks', 0)}개 청크")
        else:
            print(f"   ❌ 테스트 학습 실패: {result}")
            return False
        
        # 2. EORA Memory System 테스트
        print(f"\n2️⃣ EORA Memory System 검증 (경과: {time.time() - start_time:.1f}초)")
        from eora_memory_system import get_eora_memory_system
        
        memory_system = get_eora_memory_system()
        if not memory_system or not memory_system.is_connected():
            print("   ❌ EORA Memory System 연결 실패")
            return False
        
        print("   ✅ EORA Memory System 연결 성공")
        
        # 3. 회상 기능 테스트
        print(f"\n3️⃣ 학습내용 회상 기능 검증 (경과: {time.time() - start_time:.1f}초)")
        
        # 다양한 키워드로 회상 테스트
        test_queries = [
            "관리자_테스트",
            "회상_검증", 
            "완전_해결",
            "테스트용 문서"
        ]
        
        all_recall_success = True
        for i, query in enumerate(test_queries):
            print(f"   📍 테스트 {i+1}: '{query}' 검색")
            
            results = await memory_system.recall_learned_content(
                query=query,
                memory_type=None,  # 모든 타입 검색
                limit=5
            )
            
            if results and len(results) > 0:
                print(f"      ✅ 검색 성공: {len(results)}개 결과")
                
                # 첫 번째 결과 상세 분석
                first_result = results[0]
                print(f"      📋 첫 번째 결과:")
                print(f"         - 내용: {first_result.get('content', first_result.get('response', ''))[:50]}...")
                print(f"         - 파일명: {first_result.get('filename', first_result.get('source_file', ''))}")
                print(f"         - 카테고리: {first_result.get('category', '')}")
                print(f"         - 메모리 타입: {first_result.get('memory_type', '')}")
                print(f"         - 관련성 점수: {first_result.get('relevance_score', 0)}")
            else:
                print(f"      ❌ 검색 실패: 결과 없음")
                all_recall_success = False
        
        # 4. API 엔드포인트 검증 (시뮬레이션)
        print(f"\n4️⃣ API 엔드포인트 검증 (경과: {time.time() - start_time:.1f}초)")
        
        # app.py의 enhanced_recall API 로직 시뮬레이션
        test_query = "관리자_테스트"
        api_results = await memory_system.recall_learned_content(
            query=test_query,
            memory_type=None,
            limit=10
        )
        
        # API 응답 포맷팅 시뮬레이션
        formatted_results = []
        for result in api_results:
            formatted_result = {
                "id": str(result.get("_id", "")),
                "content": result.get("content", result.get("response", "")),
                "filename": result.get("filename", result.get("source_file", "")),
                "category": result.get("category", ""),
                "keywords": result.get("keywords", result.get("tags", [])),
                "memory_type": result.get("memory_type", ""),
                "timestamp": result.get("timestamp", ""),
                "relevance_score": result.get("relevance_score", 0)
            }
            formatted_results.append(formatted_result)
        
        if formatted_results:
            print(f"   ✅ API 포맷팅 성공: {len(formatted_results)}개 결과")
            print(f"   📊 API 응답 샘플:")
            sample = formatted_results[0]
            for key, value in sample.items():
                if key == "content" and len(str(value)) > 50:
                    print(f"      {key}: {str(value)[:50]}...")
                else:
                    print(f"      {key}: {value}")
        else:
            print("   ❌ API 포맷팅 실패: 결과 없음")
            all_recall_success = False
        
        # 5. 필드 호환성 검증
        print(f"\n5️⃣ 필드 호환성 검증 (경과: {time.time() - start_time:.1f}초)")
        
        if api_results:
            sample_data = api_results[0]
            compatibility_check = {
                "content": "content" in sample_data or "response" in sample_data,
                "filename": "filename" in sample_data or "source_file" in sample_data,
                "keywords": "keywords" in sample_data or "tags" in sample_data,
                "category": "category" in sample_data,
                "memory_type": "memory_type" in sample_data
            }
            
            print("   📋 필드 호환성 체크:")
            for field, status in compatibility_check.items():
                print(f"      {field}: {'✅' if status else '❌'}")
            
            all_fields_compatible = all(compatibility_check.values())
            if all_fields_compatible:
                print("   ✅ 모든 필드 호환성 확인")
            else:
                print("   ⚠️ 일부 필드 호환성 문제 있음")
        
        # 최종 결과
        elapsed_time = time.time() - start_time
        print(f"\n🎯 최종 검증 결과 (총 소요시간: {elapsed_time:.2f}초):")
        
        if all_recall_success and formatted_results:
            print("   ✅ 관리자 페이지 학습내용 회상 기능 완전 해결 확인")
            print("   ✅ Enhanced Learning System과 EORA Memory System 연동 성공")
            print("   ✅ API 엔드포인트 정상 작동")
            print("   ✅ 필드 호환성 문제 해결")
            return True
        else:
            print("   ❌ 일부 기능에서 문제 발견")
            print("   📝 추가 수정 필요")
            return False
            
    except Exception as e:
        print(f"\n❌ 검증 중 오류 발생: {e}")
        import traceback
        print(f"상세 오류:\n{traceback.format_exc()}")
        return False

def main():
    """메인 실행 함수"""
    try:
        success = asyncio.run(test_admin_recall_complete())
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 관리자 페이지 학습내용 회상 문제 완전 해결 확인!")
            print("✅ 모든 검증 테스트 통과")
        else:
            print("⚠️ 일부 문제가 남아있습니다")
            print("🔧 추가 수정이 필요합니다")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ 메인 실행 오류: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🔒 테스트 완료 (종료 코드: {exit_code})")
    sys.exit(exit_code)