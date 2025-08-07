import requests
import json
from datetime import datetime

def test_memory_storage():
    """학습된 메모리 데이터 저장 확인 테스트"""
    
    base_url = "http://127.0.0.1:8002"
    print("🔍 학습된 데이터 검증 시작...")
    print(f"📡 서버 URL: {base_url}")
    print("=" * 50)
    
    try:
        # 1. 아우라 메모리 통계 확인
        print("1️⃣ 아우라 메모리 통계 확인...")
        stats_response = requests.get(f"{base_url}/api/aura/memory/stats", timeout=10)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"✅ 통계 조회 성공:")
            print(f"   📊 총 메모리 개수: {stats_data.get('total_memories', 0):,}개")
            print(f"   💾 메모리 시스템: {stats_data.get('system', 'Unknown')}")
        else:
            print(f"❌ 통계 조회 실패: {stats_response.status_code}")
            print(f"   응답: {stats_response.text}")
        
        print()
        
        # 2. 학습된 메모리 회상 테스트
        print("2️⃣ 학습된 메모리 회상 테스트...")
        
        test_queries = [
            "금강", 
            "영업시간",
            "심리상담",
            "상담",
            "시간"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"   🔍 테스트 {i}: '{query}' 검색...")
            
            recall_response = requests.get(
                f"{base_url}/api/aura/recall",
                params={"query": query, "recall_type": "normal"},
                timeout=10
            )
            
            if recall_response.status_code == 200:
                recall_data = recall_response.json()
                memories = recall_data.get('memories', [])
                print(f"   ✅ 검색 성공: {len(memories)}개 메모리 발견")
                
                # 첫 번째 메모리 미리보기
                if memories:
                    first_memory = memories[0]
                    content = first_memory.get('content', first_memory.get('message', ''))[:100]
                    print(f"   📝 첫 번째 결과 미리보기: {content}...")
                else:
                    print("   ℹ️ 해당 키워드로 검색된 메모리가 없습니다.")
            else:
                print(f"   ❌ 검색 실패: {recall_response.status_code}")
                print(f"      응답: {recall_response.text[:200]}...")
        
        print()
        
        # 3. 메모리 리스트 확인
        print("3️⃣ 메모리 전체 리스트 확인...")
        memory_list_response = requests.get(f"{base_url}/api/aura/memory", timeout=10)
        
        if memory_list_response.status_code == 200:
            memory_list_data = memory_list_response.json()
            memories = memory_list_data.get('memories', [])
            print(f"✅ 메모리 리스트 조회 성공: {len(memories)}개")
            
            # 최신 메모리 5개 미리보기
            if memories:
                print("   📋 최신 메모리 5개 미리보기:")
                for i, memory in enumerate(memories[:5], 1):
                    content = memory.get('content', memory.get('message', ''))[:80]
                    timestamp = memory.get('timestamp', 'Unknown')
                    memory_type = memory.get('memory_type', 'Unknown')
                    print(f"      {i}. [{memory_type}] {content}... ({timestamp})")
        else:
            print(f"❌ 메모리 리스트 조회 실패: {memory_list_response.status_code}")
            print(f"   응답: {memory_list_response.text[:200]}...")
        
        print()
        print("=" * 50)
        print("🎯 테스트 완료!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패!")
        print("   서버가 실행 중인지 확인해주세요.")
        print("   예상 URL: http://127.0.0.1:8002")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과!")
        print("   서버 응답이 너무 느립니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

def test_chat_with_learned_data():
    """학습된 데이터를 활용한 대화 테스트"""
    
    base_url = "http://127.0.0.1:8002"
    print("\n🤖 학습된 데이터 활용 대화 테스트...")
    print("=" * 50)
    
    test_messages = [
        "영업시간이 언제인가요?",
        "상담 받고 싶어요",
        "우울해요",
        "금강에 대해 설명해주세요"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"{i}️⃣ 테스트 질문: '{message}'")
        
        try:
            chat_data = {
                "message": message,
                "session_id": f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user_id": "test_user"
            }
            
            chat_response = requests.post(
                f"{base_url}/api/chat",
                json=chat_data,
                timeout=30
            )
            
            if chat_response.status_code == 200:
                response_data = chat_response.json()
                ai_response = response_data.get('response', '')
                recalled_count = len(response_data.get('recalled_memories', []))
                
                print(f"   ✅ 응답 성공")
                print(f"   🧠 회상된 메모리: {recalled_count}개")
                print(f"   💬 AI 응답: {ai_response[:200]}...")
                if len(ai_response) > 200:
                    print("      (응답이 200자를 초과하여 생략됨)")
            else:
                print(f"   ❌ 응답 실패: {chat_response.status_code}")
                print(f"      오류 내용: {chat_response.text[:100]}...")
        
        except Exception as e:
            print(f"   ❌ 오류 발생: {e}")
        
        print()

if __name__ == "__main__":
    test_memory_storage()
    test_chat_with_learned_data() 