"""
EORA 사용자별 맞춤 기억 정책 생성기
- 강화/망각 조건을 개인 패턴에 따라 조정
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from eora_memory.eora_self_learning_pattern_analyzer import analyze_user_patterns

def get_user_memory_policy(user_id="default_user"):
    pattern = analyze_user_patterns(user_id)

    policy = {
        "strengthen_threshold": 0.05,
        "forget_threshold": 60,
        "importance_range": (1000, 10000)
    }

    if pattern["avg_recovery_delay"] > 5:
        policy["forget_threshold"] += 15  # 더 오래 기억 유지

    if pattern["belief_change_count"] >= 5:
        policy["strengthen_threshold"] += 0.02  # 더 적극적 강화

    print(f"✅ 사용자 맞춤 정책 적용 완료: {policy}")
    return policy

if __name__ == "__main__":
    get_user_memory_policy()