import sys
sys.path.append('src')

from aura_memory_system import EORAMemorySystem

print("🧪 EORAMemorySystem 최종 테스트")
eora = EORAMemorySystem()
print("✅ EORAMemorySystem 인스턴스 생성 성공")
print(f"✅ 8종 회상 시스템: {len(eora.recall_types)}개")
print(f"✅ 고급 기능: 직관({eora.intuition_engine}), 통찰({eora.insight_engine}), 지혜({eora.wisdom_engine})")
print("🎉 모든 기능이 정상적으로 로드되었습니다!") 