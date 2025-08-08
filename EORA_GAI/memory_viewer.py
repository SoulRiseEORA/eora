# memory_viewer.py - 향상된 메모리 뷰어

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from tabulate import tabulate

# EORA 시스템 import
from EORA_Consciousness_AI import EORA

class MemoryViewer:
    def __init__(self, memory_path='memory_trace.json'):
        """메모리 뷰어 초기화"""
        self.memory_path = memory_path
        self.eora = None
        self.try_initialize_eora()

    def try_initialize_eora(self):
        """EORA 시스템 초기화 시도"""
        try:
            self.eora = EORA(memory_path=self.memory_path)
            print("✅ EORA 시스템 연결 완료")
        except Exception as e:
            print(f"⚠️ EORA 시스템 연결 실패: {str(e)}")
            self.eora = None

    def load_legacy_memory(self) -> List[Dict]:
        """기존 형식 메모리 로드"""
        try:
            if Path(self.memory_path).exists():
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('loops', [])
            else:
                print("❌ memory_trace.json 파일이 존재하지 않습니다.")
                return []
        except Exception as e:
            print(f"⚠️ 메모리 로드 실패: {str(e)}")
            return []

    async def load_new_memory(self, query: str = None, limit: int = 50) -> List[Dict]:
        """새 형식 메모리 로드"""
        try:
            if self.eora:
                return await self.eora.recall_memory(query, limit)
            else:
                return []
        except Exception as e:
            print(f"⚠️ 새 메모리 로드 실패: {str(e)}")
            return []

    def display_legacy_summary(self, memory: List[Dict]) -> None:
        """기존 형식 메모리 요약 표시"""
        if not memory:
            print("📝 표시할 메모리가 없습니다.")
            return

        headers = ["회차", "질문", "EORA 응답 (요약)", "MiniAI 감정", "충돌"]
        table = []

        for i, loop in enumerate(memory, 1):
            user_input = loop.get('user_input', '')[:20] + ("..." if len(loop.get('user_input', '')) > 20 else "")
            eora_response = loop.get('eora_response', '')[:30] + ("..." if len(loop.get('eora_response', '')) > 30 else "")
            table.append([
                i,
                user_input,
                eora_response,
                loop.get('emotion_level', 0.0),
                "⚠️" if loop.get('conflict', False) else ""
            ])

        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

    def display_new_summary(self, memory: List[Dict]) -> None:
        """새 형식 메모리 요약 표시"""
        if not memory:
            print("📝 표시할 메모리가 없습니다.")
            return

        headers = ["ID", "시간", "질문", "응답 타입", "감정", "에너지", "스트레스"]
        table = []

        for memory_item in memory:
            user_input = memory_item.get('user_input', '')[:25] + ("..." if len(memory_item.get('user_input', '')) > 25 else "")
            response = memory_item.get('response', {})
            system_state = response.get('system_state', {})
            
            # 시간 포맷팅
            timestamp = memory_item.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m-%d %H:%M')
                except:
                    time_str = timestamp[:16]
            else:
                time_str = "N/A"

            table.append([
                memory_item.get('id', '')[:8] + "...",
                time_str,
                user_input,
                response.get('response_type', 'unknown'),
                system_state.get('emotion', 'neutral'),
                f"{system_state.get('energy', 0.0):.2f}",
                f"{system_state.get('stress', 0.0):.2f}"
            ])

        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

    async def display_detailed_memory(self, memory_id: str) -> None:
        """특정 메모리 상세 표시"""
        try:
            if not self.eora:
                print("❌ EORA 시스템이 연결되지 않았습니다.")
                return

            # 메모리 검색
            memories = await self.eora.recall_memory()
            target_memory = None
            
            for memory in memories:
                if memory.get('id', '').startswith(memory_id):
                    target_memory = memory
                    break

            if not target_memory:
                print(f"❌ ID '{memory_id}'의 메모리를 찾을 수 없습니다.")
                return

            # 상세 정보 표시
            print("\n" + "="*60)
            print("📋 메모리 상세 정보")
            print("="*60)
            
            print(f"ID: {target_memory.get('id', 'N/A')}")
            print(f"시간: {target_memory.get('timestamp', 'N/A')}")
            print(f"세션: {target_memory.get('session_id', 'N/A')}")
            print("-"*60)
            
            print("사용자 입력:")
            print(f"  {target_memory.get('user_input', 'N/A')}")
            print("-"*60)
            
            response = target_memory.get('response', {})
            print("시스템 응답:")
            print(f"  {response.get('response', 'N/A')}")
            print(f"  타입: {response.get('response_type', 'N/A')}")
            print("-"*60)
            
            system_state = response.get('system_state', {})
            print("시스템 상태:")
            print(f"  감정: {system_state.get('emotion', 'N/A')}")
            print(f"  에너지: {system_state.get('energy', 0.0):.2f}")
            print(f"  스트레스: {system_state.get('stress', 0.0):.2f}")
            print(f"  고통: {system_state.get('pain', 0.0):.2f}")
            print("-"*60)
            
            # 분석 결과 표시
            analyses = response.get('analyses', {})
            if analyses:
                print("분석 결과:")
                for analysis_type, analysis_data in analyses.items():
                    if isinstance(analysis_data, dict):
                        print(f"  {analysis_type}:")
                        for key, value in analysis_data.items():
                            if key != 'timestamp':
                                print(f"    {key}: {value}")
                print("-"*60)

        except Exception as e:
            print(f"⚠️ 메모리 상세 표시 중 오류: {str(e)}")

    async def display_memory_statistics(self) -> None:
        """메모리 통계 표시"""
        try:
            if not self.eora:
                print("❌ EORA 시스템이 연결되지 않았습니다.")
                return

            stats = self.eora.get_memory_statistics()
            
            print("\n" + "="*60)
            print("📊 메모리 통계")
            print("="*60)
            
            print(f"총 메모리 수: {stats.get('total_memories', 0)}")
            print(f"가장 오래된 메모리: {stats.get('oldest_memory', 'N/A')}")
            print(f"가장 최근 메모리: {stats.get('newest_memory', 'N/A')}")
            
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
            
            print("="*60)

        except Exception as e:
            print(f"⚠️ 통계 표시 중 오류: {str(e)}")

    async def search_memories(self, query: str, limit: int = 10) -> None:
        """메모리 검색"""
        try:
            if not self.eora:
                print("❌ EORA 시스템이 연결되지 않았습니다.")
                return

            print(f"\n🔍 '{query}' 검색 결과:")
            memories = await self.eora.recall_memory(query, limit)
            
            if memories:
                self.display_new_summary(memories)
            else:
                print("📝 검색 결과가 없습니다.")

        except Exception as e:
            print(f"⚠️ 메모리 검색 중 오류: {str(e)}")

    async def search_by_emotion(self, emotion: str, limit: int = 10) -> None:
        """감정 기반 메모리 검색"""
        try:
            if not self.eora:
                print("❌ EORA 시스템이 연결되지 않았습니다.")
                return

            print(f"\n😊 '{emotion}' 감정 관련 메모리:")
            memories = await self.eora.search_memories_by_emotion(emotion, limit)
            
            if memories:
                self.display_new_summary(memories)
            else:
                print("📝 해당 감정의 메모리가 없습니다.")

        except Exception as e:
            print(f"⚠️ 감정 기반 검색 중 오류: {str(e)}")

    async def search_by_resonance(self, min_resonance: float = 0.5, limit: int = 10) -> None:
        """공명 점수 기반 메모리 검색"""
        try:
            if not self.eora:
                print("❌ EORA 시스템이 연결되지 않았습니다.")
                return

            print(f"\n⚡ 공명 점수 {min_resonance} 이상 메모리:")
            memories = await self.eora.search_memories_by_resonance(min_resonance, limit)
            
            if memories:
                self.display_new_summary(memories)
            else:
                print("📝 해당 공명 점수의 메모리가 없습니다.")

        except Exception as e:
            print(f"⚠️ 공명 기반 검색 중 오류: {str(e)}")

    def display_system_status(self) -> None:
        """시스템 상태 표시"""
        try:
            if not self.eora:
                print("❌ EORA 시스템이 연결되지 않았습니다.")
                return

            status = self.eora.get_system_status()
            
            print("\n" + "="*60)
            print("🔧 시스템 상태")
            print("="*60)
            
            core_system = status.get('core_system', {})
            system_state = core_system.get('system_state', {})
            
            print(f"시스템 활성화: {'✅' if system_state.get('active', False) else '❌'}")
            print(f"시스템 건강도: {system_state.get('health', 0.0):.2f}")
            print(f"시작 시간: {system_state.get('start_time', 'N/A')}")
            print(f"마지막 업데이트: {system_state.get('last_update', 'N/A')}")
            print(f"메모리 수: {core_system.get('memory_count', 0)}")
            print(f"오류 수: {core_system.get('error_count', 0)}")
            print(f"시스템 버전: {status.get('system_version', 'N/A')}")
            
            print("="*60)

        except Exception as e:
            print(f"⚠️ 시스템 상태 표시 중 오류: {str(e)}")

async def main():
    """메인 함수"""
    viewer = MemoryViewer()
    
    print("🧠 EORA 메모리 뷰어")
    print("="*60)
    
    while True:
        print("\n📋 메뉴:")
        print("1. 기존 메모리 요약 보기")
        print("2. 새 메모리 요약 보기")
        print("3. 메모리 검색")
        print("4. 감정 기반 검색")
        print("5. 공명 기반 검색")
        print("6. 메모리 통계")
        print("7. 시스템 상태")
        print("8. 특정 메모리 상세 보기")
        print("0. 종료")
        
        choice = input("\n선택하세요 (0-8): ").strip()
        
        if choice == "0":
            print("👋 메모리 뷰어를 종료합니다.")
            break
        elif choice == "1":
            memory = viewer.load_legacy_memory()
            viewer.display_legacy_summary(memory)
        elif choice == "2":
            memory = await viewer.load_new_memory()
            viewer.display_new_summary(memory)
        elif choice == "3":
            query = input("검색어를 입력하세요: ").strip()
            if query:
                await viewer.search_memories(query)
        elif choice == "4":
            emotion = input("감정을 입력하세요 (예: joy, sadness, anger): ").strip()
            if emotion:
                await viewer.search_by_emotion(emotion)
        elif choice == "5":
            try:
                resonance = float(input("최소 공명 점수를 입력하세요 (0.0-1.0): ").strip())
                await viewer.search_by_resonance(resonance)
            except ValueError:
                print("❌ 올바른 숫자를 입력하세요.")
        elif choice == "6":
            await viewer.display_memory_statistics()
        elif choice == "7":
            viewer.display_system_status()
        elif choice == "8":
            memory_id = input("메모리 ID를 입력하세요: ").strip()
            if memory_id:
                await viewer.display_detailed_memory(memory_id)
        else:
            print("❌ 올바른 선택지를 입력하세요.")

if __name__ == "__main__":
    asyncio.run(main())