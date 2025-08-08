"""
hybrid_recall_manager.py

🧠 다중 회상 전략 자동 판단 및 우선순위 병렬 적용 모듈
- 정규 회상 (태그, 벡터)
- 망각 기반 필터
- 반사적 1회성 회상
- 유사 회상 생성 보완
- 기억 계보 추적
- 자기 vs 타인 회상 분리

"""

from aura_system.meta_store import (
    search_atoms_by_tags,
    get_fade_candidates,
    get_reflex_memories,
    get_memory_lineage
)
from aura_system.memory_structurer import load_memory_db
from openai import OpenAI
import os

# 통합 API 키 검색 사용
api_key = _get_valid_openai_key() if '_get_valid_openai_key' in globals() else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ✅ 우선순위 회상 판단 및 실행
def hybrid_recall(user_input: str, tags: list, atom_id: str = None, context: dict = None, emotion: dict = None, belief: dict = None, wisdom: dict = None, eora: dict = None, system: dict = None) -> dict:
    result = {
        "reflex": [],
        "direct": [],
        "fading": [],
        "lineage": [],
        "fallback": "",
        "context": context,
        "emotion": emotion,
        "belief": belief,
        "wisdom": wisdom,
        "eora": eora,
        "system": system
    }

    # 1. 즉시 반응 기억 우선 탐색
    for word in tags:
        reflex_hits = get_reflex_memories(word)
        if reflex_hits:
            result["reflex"].extend(reflex_hits)

    # 2. 태그 기반 정규 회상
    result["direct"] = search_atoms_by_tags(tags, limit=5)

    # 3. 망각 경계선에 있는 중요치 않은 기억 확인
    result["fading"] = get_fade_candidates(threshold=0.85)

    # 4. 계보 추적 (선택적)
    if atom_id:
        result["lineage"] = get_memory_lineage(atom_id)

    # 5. 회상 실패 시 유사 보완 제안
    if not result["direct"] and not result["reflex"]:
        messages = [
            {"role": "system", "content": "과거의 대화를 기억할 수 없다면 비슷한 이야기를 상상하여 응답을 생성해줘."},
            {"role": "user", "content": user_input}
        ]
        
        # 컨텍스트 정보 추가
        if context:
            messages.append({"role": "system", "content": f"[컨텍스트]\n{context}"})
        
        # 감정 정보 추가
        if emotion:
            messages.append({"role": "system", "content": f"[감정]\n{emotion}"})
        
        # 신념 정보 추가
        if belief:
            messages.append({"role": "system", "content": f"[신념]\n{belief}"})
        
        # 지혜 정보 추가
        if wisdom:
            messages.append({"role": "system", "content": f"[지혜]\n{wisdom}"})
        
        # 이오라 정보 추가
        if eora:
            messages.append({"role": "system", "content": f"[이오라]\n{eora}"})
        
        # 시스템 정보 추가
        if system:
            messages.append({"role": "system", "content": f"[시스템]\n{system}"})
        
        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300
            )
            result["fallback"] = completion.choices[0].message.content
        except Exception as e:
            result["fallback"] = f"[GPT fallback 오류]: {str(e)}"

    return result