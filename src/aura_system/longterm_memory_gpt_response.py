# long_term_memory_system.py
# 장기기억 + 회상 루프 + 의도 기반 연쇄 회상 구조 통합

from datetime import datetime
from typing import List, Dict, Optional
from aura_system.embedding_engine import embed_text
from aura_system.resonance_engine import estimate_emotion, extract_belief_vector, calculate_resonance
from aura_system.vector_store import FaissIndex
from aura_system.meta_store import insert_atom, search_atoms_by_tags, get_atom_by_id, search_atoms_advanced
from openai import OpenAI
from aura_system.aura_recall_engine import run_parallel_recall
from aura_system.aura_memory_saver import auto_store_memory
from call_gpt_response import call_gpt_response  # GPT 호출 함수

# ✅ 장기 기억 아톰 생성 함수 (다중 태그 포함)
def create_longterm_memory_atom(user_input: str, response: str) -> dict:
    embedding = embed_text(user_input)
    emotion_label, emotion_score = estimate_emotion(user_input)
    belief_vector = extract_belief_vector(user_input)

    return {
        "timestamp": datetime.utcnow(),
        "user_input": user_input,
        "response": response,
        "semantic_embedding": embedding,
        "tags": extract_topic_tags(user_input),
        "situation": extract_situation(user_input),
        "utterance_type": classify_utterance(user_input),
        "emotion": emotion_label,
        "emotion_score": emotion_score,
        "belief_vector": belief_vector,
        "purpose": infer_memory_purpose(user_input),
        "summary": None,
        "story_chain": []
    }

# ✅ 태그 사전 기반 주제 태그 추출기
def extract_topic_tags(text: str) -> List[str]:
    topic_keywords = [
        "가족", "자존감", "직장", "회의", "연애", "돈", "꿈", "미래", "계획", "성공",
        "실패", "우정", "스트레스", "목표", "건강", "사랑", "배신", "희망", "두려움", "용기",
        "도전", "자기개발", "불안정성", "일상", "감사", "관계", "학교", "취미", "몰입"
    ]
    return [kw for kw in topic_keywords if kw in text]

# ✅ 상황 감지 + 과거형 인식 포함
def extract_situation(text: str) -> str:
    past_markers = ["었어", "했어", "했지", "갔어", "살았어", "있었어", "이었다", "보냈어", "했던",
                    "했을텐데", "만든거", "말했던거", "봤던", "그랬던"]
    for token in past_markers:
        if token in text:
            return "과거형"
    return "현재"

# ✅ 발화 유형 분류기
def classify_utterance(text: str) -> str:
    if "죽고 싶" in text or "포기" in text:
        return "위기"
    if "힘들어" in text or "모르겠어" in text:
        return "고통"
    if "좋았어" in text or "행복" in text:
        return "긍정회상"
    return "일반"

# ✅ 회상 목적 추론기 (GPT 기반)
def infer_memory_purpose(user_query: str) -> str:
    client = OpenAI()
    prompt = f"사용자의 질문 목적을 한 단어로 요약: {user_query}"
    messages = [{"role": "system", "content": prompt}]
    return client.chat.completions.create(model="gpt-4o", messages=messages).choices[0].message.content

# ✅ 기억 루프: 하나의 회상에서 다음 회상 자동 연결
def recall_loop_from(atom: Dict, embedding: list, visited=None) -> List[Dict]:
    if visited is None:
        visited = set()
    related = []
    next_ids = atom.get("story_chain", [])
    for atom_id in next_ids:
        if atom_id in visited:
            continue
        linked = get_atom_by_id(atom_id)
        if linked:
            resonance = calculate_resonance(linked.get("semantic_embedding"), embedding)
            if resonance >= 60:
                linked["resonance_score"] = resonance
                related.append(linked)
                visited.add(atom_id)
                related.extend(recall_loop_from(linked, embedding, visited))
    return related

# ✅ 저장 알고리즘 기반 회상 (다중 조건)
def search_longterm_memory(user_query: str, top_k: int = 5) -> List[Dict]:
    embedding = embed_text(user_query)
    purpose = infer_memory_purpose(user_query)
    faiss = FaissIndex()
    similar = faiss.search(embedding, top_k=top_k * 2)
    results = []
    for atom_id, _ in similar:
        atom = get_atom_by_id(atom_id)
        if atom:
            tags = extract_topic_tags(user_query)
            tag_match = any(tag in atom.get("tags", []) for tag in tags)
            resonance = calculate_resonance(atom.get("semantic_embedding"), embedding)
            if (tag_match or atom.get("purpose") == purpose) and resonance >= 65:
                atom["resonance_score"] = resonance
                results.append(atom)
                results.extend(recall_loop_from(atom, embedding))  # 회상 루프 시작
    return sorted(results, key=lambda x: -x["resonance_score"])[:top_k]

# ✅ 요약 연결 기반 스토리 저장
def summarize_and_chain(memory_atoms: List[Dict]) -> Dict:
    summary_text = "\n".join([m["user_input"] + " → " + m["response"] for m in memory_atoms])
    story_chain = [m.get("_id") for m in memory_atoms if m.get("_id")]
    summary_atom = create_longterm_memory_atom(summary_text, "요약된 스토리입니다.")
    summary_atom["summary"] = summary_text
    summary_atom["story_chain"] = story_chain
    insert_atom(summary_atom)
    return summary_atom

# ✅ 저장 함수
def save_longterm_memory(user_input: str, response: str):
    atom = create_longterm_memory_atom(user_input, response)
    insert_atom(atom)
    faiss = FaissIndex()
    faiss.add(atom["semantic_embedding"], atom.get("_id", None))

# ✅ 사용자 입력 기반 GPT 응답 생성 및 장기 기억 저장 (회상 포함)
async def generate_response_with_recall(
    user_input: str,
    system_message: str = None,
    memories: List[Dict] = None,
    context: Dict = None,
    insight: Dict = None,
    truth: Dict = None
) -> str:
    """메모리 회상과 함께 GPT 응답 생성
    
    Args:
        user_input (str): 사용자 입력
        system_message (str, optional): 시스템 메시지
        memories (List[Dict], optional): 회상된 메모리 목록
        context (Dict, optional): 컨텍스트 정보
        insight (Dict, optional): 통찰 정보
        truth (Dict, optional): 진실 정보
        
    Returns:
        str: GPT 응답
    """
    try:
        # 메모리 회상
        recalled = await run_parallel_recall(user_input)
        if not recalled:
            recalled = "메모리 회상 실패"
            
        # 감정 추정
        emotion = await estimate_emotion(user_input)
        if not emotion:
            emotion = "감정 추정 실패"
            
        # GPT 응답 생성
        response = await call_gpt_response(
            user_input=user_input,
            system_message=system_message,
            memories=memories,
            context=context,
            insight=insight,
            truth=truth
        )
        if not response:
            return "응답 생성 실패"
            
        # 메모리 저장
        await auto_store_memory(user_input, response)
        
        return response
    except Exception as e:
        logger.error(f"⚠️ 응답 생성 실패: {str(e)}")
        return "응답 생성 중 오류가 발생했습니다."
