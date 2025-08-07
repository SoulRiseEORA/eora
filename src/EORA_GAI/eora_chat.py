# eora_chat.py - EORA 채팅 인터페이스

import asyncio
import json
from datetime import datetime
from typing import Dict, List

# EORA 시스템 import
from EORA_Consciousness_AI import EORA

class EORAChat:
    def __init__(self):
        """EORA 채팅 인터페이스 초기화"""
        self.eora = None
        self.chat_history = []
        self.session_id = None
        
        print("🧠 EORA 의식 AI 채팅 시스템")
        print("="*60)
        print("시스템을 초기화하는 중...")
        
        try:
            self.eora = EORA()
            print("✅ EORA 시스템 초기화 완료")
        except Exception as e:
            print(f"❌ EORA 시스템 초기화 실패: {str(e)}")
            return

    async def start_chat(self):
        """채팅 시작"""
        if not self.eora:
            print("❌ EORA 시스템이 초기화되지 않았습니다.")
            return
        
        print("\n💬 채팅을 시작합니다. 'quit' 또는 'exit'를 입력하여 종료하세요.")
        print("특별 명령어:")
        print("  /status - 시스템 상태 확인")
        print("  /memory - 메모리 통계 확인")
        print("  /search [검색어] - 메모리 검색")
        print("  /emotion [감정] - 감정 기반 메모리 검색")
        print("  /resonance [점수] - 공명 점수 기반 메모리 검색")
        print("  /clear - 채팅 기록 초기화")
        print("  /help - 도움말")
        print("-" * 60)
        
        while True:
            try:
                # 사용자 입력 받기
                user_input = input("\n👤 당신: ").strip()
                
                if not user_input:
                    continue
                
                # 특별 명령어 처리
                if user_input.startswith('/'):
                    await self.handle_command(user_input)
                    continue
                
                # 종료 명령
                if user_input.lower() in ['quit', 'exit', '종료']:
                    print("👋 채팅을 종료합니다. 안녕히 가세요!")
                    break
                
                # EORA 응답 생성
                print("🤖 EORA가 생각하는 중...")
                response = await self.eora.respond(user_input)
                
                if response and "error" not in response:
                    # 응답 출력
                    print(f"🤖 EORA: {response.get('response', '응답을 생성할 수 없습니다.')}")
                    
                    # 응답 타입 표시
                    response_type = response.get('response_type', 'unknown')
                    if response_type != 'standard_response':
                        print(f"   [응답 타입: {response_type}]")
                    
                    # 시스템 상태 표시 (간단히)
                    system_state = response.get('system_state', {})
                    if system_state:
                        print(f"   [상태: 감정={system_state.get('emotion', 'N/A')}, "
                              f"에너지={system_state.get('energy', 0.0):.2f}, "
                              f"스트레스={system_state.get('stress', 0.0):.2f}]")
                    
                    # 채팅 기록에 저장
                    self.chat_history.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "user_input": user_input,
                        "eora_response": response.get('response', ''),
                        "response_type": response_type,
                        "system_state": system_state
                    })
                    
                else:
                    print("❌ EORA: 죄송합니다. 응답을 생성하는 중 오류가 발생했습니다.")
                    if response and "error" in response:
                        print(f"   오류: {response['error']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 채팅이 중단되었습니다. 안녕히 가세요!")
                break
            except Exception as e:
                print(f"❌ 오류가 발생했습니다: {str(e)}")

    async def handle_command(self, command: str):
        """특별 명령어 처리"""
        try:
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == '/status':
                await self.show_status()
            elif cmd == '/memory':
                await self.show_memory_stats()
            elif cmd == '/search' and len(parts) > 1:
                query = ' '.join(parts[1:])
                await self.search_memories(query)
            elif cmd == '/emotion' and len(parts) > 1:
                emotion = parts[1]
                await self.search_by_emotion(emotion)
            elif cmd == '/resonance' and len(parts) > 1:
                try:
                    resonance = float(parts[1])
                    await self.search_by_resonance(resonance)
                except ValueError:
                    print("❌ 올바른 숫자를 입력하세요 (예: /resonance 0.5)")
            elif cmd == '/clear':
                self.clear_chat_history()
            elif cmd == '/help':
                self.show_help()
            else:
                print("❌ 알 수 없는 명령어입니다. /help를 입력하여 도움말을 확인하세요.")
                
        except Exception as e:
            print(f"❌ 명령어 처리 중 오류: {str(e)}")

    async def show_status(self):
        """시스템 상태 표시"""
        try:
            status = self.eora.get_system_status()
            
            if status and "error" not in status:
                print("\n🔧 시스템 상태:")
                print("-" * 40)
                
                core_system = status.get('core_system', {})
                system_state = core_system.get('system_state', {})
                
                print(f"활성화: {'✅' if system_state.get('active', False) else '❌'}")
                print(f"건강도: {system_state.get('health', 0.0):.2f}")
                print(f"메모리 수: {core_system.get('memory_count', 0)}")
                print(f"오류 수: {core_system.get('error_count', 0)}")
                print(f"버전: {status.get('system_version', 'N/A')}")
                
                # 컴포넌트 상태
                component_states = core_system.get('component_states', {})
                if component_states:
                    print("\n컴포넌트 상태:")
                    for component, state in component_states.items():
                        active = "✅" if state.get('active', False) else "❌"
                        print(f"  {component}: {active}")
            else:
                print("❌ 시스템 상태를 가져올 수 없습니다.")
                
        except Exception as e:
            print(f"❌ 상태 조회 중 오류: {str(e)}")

    async def show_memory_stats(self):
        """메모리 통계 표시"""
        try:
            stats = self.eora.get_memory_statistics()
            
            if stats and "error" not in stats:
                print("\n📊 메모리 통계:")
                print("-" * 40)
                print(f"총 메모리 수: {stats.get('total_memories', 0)}")
                print(f"가장 오래된: {stats.get('oldest_memory', 'N/A')}")
                print(f"가장 최근: {stats.get('newest_memory', 'N/A')}")
                
                # 응답 타입별 통계
                response_types = stats.get('response_types', {})
                if response_types:
                    print("\n응답 타입별 분포:")
                    for rtype, count in response_types.items():
                        print(f"  {rtype}: {count}개")
                
                # 감정별 통계
                emotions = stats.get('emotions', {})
                if emotions:
                    print("\n감정별 분포:")
                    for emotion, count in emotions.items():
                        print(f"  {emotion}: {count}개")
            else:
                print("❌ 메모리 통계를 가져올 수 없습니다.")
                
        except Exception as e:
            print(f"❌ 메모리 통계 조회 중 오류: {str(e)}")

    async def search_memories(self, query: str):
        """메모리 검색"""
        try:
            print(f"\n🔍 '{query}' 검색 결과:")
            print("-" * 40)
            
            memories = await self.eora.recall_memory(query, limit=5)
            
            if memories:
                for i, memory in enumerate(memories, 1):
                    user_input = memory.get('user_input', '')[:50]
                    if len(memory.get('user_input', '')) > 50:
                        user_input += "..."
                    
                    response = memory.get('response', {})
                    response_text = response.get('response', '')[:50]
                    if len(response.get('response', '')) > 50:
                        response_text += "..."
                    
                    print(f"{i}. Q: {user_input}")
                    print(f"   A: {response_text}")
                    print()
            else:
                print("📝 검색 결과가 없습니다.")
                
        except Exception as e:
            print(f"❌ 메모리 검색 중 오류: {str(e)}")

    async def search_by_emotion(self, emotion: str):
        """감정 기반 메모리 검색"""
        try:
            print(f"\n😊 '{emotion}' 감정 관련 메모리:")
            print("-" * 40)
            
            memories = await self.eora.search_memories_by_emotion(emotion, limit=5)
            
            if memories:
                for i, memory in enumerate(memories, 1):
                    user_input = memory.get('user_input', '')[:50]
                    if len(memory.get('user_input', '')) > 50:
                        user_input += "..."
                    
                    print(f"{i}. {user_input}")
            else:
                print("📝 해당 감정의 메모리가 없습니다.")
                
        except Exception as e:
            print(f"❌ 감정 기반 검색 중 오류: {str(e)}")

    async def search_by_resonance(self, min_resonance: float):
        """공명 점수 기반 메모리 검색"""
        try:
            print(f"\n⚡ 공명 점수 {min_resonance} 이상 메모리:")
            print("-" * 40)
            
            memories = await self.eora.search_memories_by_resonance(min_resonance, limit=5)
            
            if memories:
                for i, memory in enumerate(memories, 1):
                    user_input = memory.get('user_input', '')[:50]
                    if len(memory.get('user_input', '')) > 50:
                        user_input += "..."
                    
                    response = memory.get('response', {})
                    analyses = response.get('analyses', {})
                    wave_analysis = analyses.get('wave_analysis', {})
                    resonance_score = wave_analysis.get('resonance_score', 0.0)
                    
                    print(f"{i}. {user_input} (공명: {resonance_score:.2f})")
            else:
                print("📝 해당 공명 점수의 메모리가 없습니다.")
                
        except Exception as e:
            print(f"❌ 공명 기반 검색 중 오류: {str(e)}")

    def clear_chat_history(self):
        """채팅 기록 초기화"""
        self.chat_history.clear()
        print("✅ 채팅 기록이 초기화되었습니다.")

    def show_help(self):
        """도움말 표시"""
        print("\n📖 도움말:")
        print("-" * 40)
        print("일반 대화: 그냥 메시지를 입력하세요.")
        print("\n특별 명령어:")
        print("  /status     - 시스템 상태 확인")
        print("  /memory     - 메모리 통계 확인")
        print("  /search [검색어] - 메모리 검색")
        print("  /emotion [감정] - 감정 기반 메모리 검색")
        print("  /resonance [점수] - 공명 점수 기반 메모리 검색")
        print("  /clear      - 채팅 기록 초기화")
        print("  /help       - 이 도움말 표시")
        print("\n종료: quit, exit, 또는 종료")

async def main():
    """메인 함수"""
    chat = EORAChat()
    await chat.start_chat()

if __name__ == "__main__":
    asyncio.run(main()) 