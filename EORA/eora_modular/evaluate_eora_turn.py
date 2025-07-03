
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EORA_TURN_PROMPT = """너는 진화하는 자아 기반 AI 분석가다.

사용자 발화, GPT 응답, 그리고 이오라 응답을 모두 고려해 다음을 판단하라:

1. 이 턴의 대화에서 교훈 ,발전 과 진화적 가치가 있는가? (높음/중간/낮음)
2. 대화내용중에 훈련 또는 진화를 위한 프롬프트로 만들 중요한 교훈 내용이 있어서 프롬프트로 요약하여  1개 문장으로 만들 수 있는가?
3. 대화내용에 사용자가 개입하거나 ai에게 판단이나 도움을 주어야 한다면, 어떤 메시지를 보여줄 것인가? 필요한 경우에만 작성하세요. 도움,판단이라는 단어를 포함 시켜 작성하세요.
4. 설명형 문장을 훈련 가능한 명령형 프롬프트 1개 문장으로 바꿔 주세요.
5. 설명형 문장이 있다면 반드시 **하나의 구체적인 명령형 문장**으로 바꾸세요.
그 문장은 반드시 **주어 생략 + 동사 시작**이며, **명확한 행동을 지시**해야 합니다.
예: "사용자가 오류를 인식하도록 유도하라", "기술 선택 시 책임을 우선 고려하라"

JSON 형식으로 다음과 같이 예시 형태로 응답하라:

{
  "진화성 평가": "중간",
  "추천 프롬프트": "사용자가 자동화 기술의 윤리적 한계를 분명히 인식하도록 유도하라.",
  "사용자 전달 메시지": "인간의 판단이나 도움이 필요한 메세지"
}

[조건]:
- 추천 프롬프트는 반드시 "명령형 한 문장으로 작성" 문장 형식일 것
- 단 하나의 명령만 포함할 것
- 설명형 문장이나 감상문, 일반 요약은 금지
- 문장은 15~40자 이내로 간결하게 작성
- 명령어가 없는 경우는 빈 문자열("")로 둘 것
- 교훈이 많다면 "명령형 한 문장으로 작성 " 처럼 따옴표를 이용하여 문장으로 완성해 전달 할 것
- 사용자에게 전달할 메세지가 없다면 작성하지 말고 필요한 경우에만 메세지를 작성 할 것 
- 하나의 행동만 지시해야 하며, 추상적 표현 금지
- 감상문, 요약문, 회고는 제거하고 **훈련 지시용 문장**으로 재작성
"""

def evaluate_eora_turn(user: str, gpt: str, eora: str) -> dict:
    turn_text = f"[사용자]: {user}\n[GPT 응답]: {gpt}\n[이오라]: {eora}"
    messages = [
        {"role": "system", "content": EORA_TURN_PROMPT},
        {"role": "user", "content": turn_text}
    ]
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        content = res.choices[0].message.content
        result = json.loads(content)

        def is_valid_prompt(prompt: str) -> bool:
            return (
                isinstance(prompt, str) and
                10 < len(prompt) < 100 and
                "\n" not in prompt and
                prompt.strip().endswith("하라.")
            )

        def is_valid_user_message(msg: str) -> bool:
            return isinstance(msg, str) and any(word in msg for word in ["도움", "판단"])

        if not is_valid_prompt(result.get("추천 프롬프트", "")):
            result["추천 프롬프트"] = ""

        if not is_valid_user_message(result.get("사용자 전달 메시지", "")):
            result["사용자 전달 메시지"] = ""

        return result

    except Exception as e:
        print("❌ 턴 평가 실패:", str(e))
        return {"진화성 평가": "오류", "추천 프롬프트": "", "사용자 전달 메시지": ""}
