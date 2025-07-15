# ✅ 회상 메모리 포맷을 출력용으로 변환하는 함수
# MongoDB나 Redis에서 불러온 memory atom에서 텍스트 및 응답을 추출하여 정리된 회상 형식으로 반환합니다.
def format_recall(atom: dict) -> str:
    timestamp = atom.get("timestamp", "")
    user_input = atom.get("user_input", "[텍스트 없음]")
    response = atom.get("response", "[응답 없음]")
    return f"📅 {timestamp}\n📌 요약: {user_input}\n🎯 응답: {response}"

# ✅ 메모리 아톰 생성 예시
# 실제 응답 저장 시 반드시 아래와 같은 구조를 포함하도록 합니다.
atom = {
    "timestamp": datetime.utcnow(),
    "user_input": user_input,
    "response": response,
    "semantic_embedding": embed_text(user_input),
    "tags": ["날씨", "기분", "야구"],
    "emotion": "기쁨",
    "origin_type": "user"
}