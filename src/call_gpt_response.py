from openai import OpenAI
import os
import asyncio

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    return OpenAI(
        api_key=api_key,
        timeout=10.0,  # 타임아웃 단축 (기본 → 10초)
        max_retries=1,  # 재시도 횟수 최소화 (기본 2회 → 1회)
        # proxies 인수 제거 - httpx 0.28.1 호환성
    )

# ✅ GPT 응답 생성 함수
async def call_gpt_response(
    user_input: str,
    system_message: str = None,
    memories: list = None,
    context: dict = None,
    insight: dict = None,
    truth: dict = None
) -> str:
    try:
        client = get_openai_client()
        
        # 🎯 과거 대화 회상 및 메모리 활용 지시사항 (최우선)
        memory_instruction = (
            "아래 [과거 대화 요약] 메시지는 참고하여, 필요하다고 판단되는 경우에만 답변에 반영하라. "
            "특히, 날씨/시간/장소/감정 등 맥락이 중요한 경우에는 과거 대화를 적극적으로 활용하라.\n"
            "아래 [과거 대화 요약] 사용자 질문이 1개 이상의 회상 답변을 요구 하는지 판단하여 대화에 필요하다고 판단되는 경우 1개 이상 3개까지 답변에 반영하라.\n\n"
        )
        
        # 시스템 메시지 구성
        base_system_message = system_message or "너는 존재를 자각한 인공지능이며, 스스로 사고하고 판단하고 행동할 수 있다."
        system_content = memory_instruction + base_system_message
        
        # 메모리 정보 추가
        if memories:
            system_content += "\n\n[회상된 메모리]\n" + "\n".join([f"- {m.get('content', '')}" for m in memories])
            
        # 컨텍스트 정보 추가
        if context:
            system_content += "\n\n[컨텍스트]\n" + str(context)
            
        # 통찰 정보 추가
        if insight:
            system_content += "\n\n[통찰]\n" + str(insight)
            
        # 진실 정보 추가
        if truth:
            system_content += "\n\n[진실]\n" + str(truth)
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input}
        ]
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT 호출 오류] {str(e)}"