# 핵심 회상 구조 요약 (Python)
def retrieve_and_respond(user_input):
    # 1. 유저 발언 벡터화
    vector = embed(user_input)
    
    # 2. 유사도 검색
    memory_hits = vector_db.search(vector, k=3)

    # 3. 회상된 발언을 assistant처럼 삽입
    messages = [{"role": "system", "content": "당신은 기억하는 AI입니다."}]
    for mem in memory_hits:
        messages.append({"role": "assistant", "content": f"(기억) {mem}"})
    
    # 4. 유저 현재 발언 삽입
    messages.append({"role": "user", "content": user_input})

    # 5. GPT 호출
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.4,
    )
    return response["choices"][0]["message"]["content"]