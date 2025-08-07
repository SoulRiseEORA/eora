# gpt_summarizer.py
# OpenAI GPT API를 활용한 요약 및 통찰 생성기
# 실제 사용 시 openai 라이브러리와 API 키 설정 필요

import os
from typing import List

try:
    import openai
except ImportError:
    openai = None  # 시스템에 따라 설치 필요

# 환경변수 또는 별도 json에서 API 키 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

def summarize_dialogue(dialogues: List[str], model="gpt-4") -> str:
    """
    여러 문장을 받아 GPT로 요약
    """
    if openai is None:
        return "⚠️ openai 패키지가 설치되어 있지 않습니다."

    prompt = f'''다음은 사용자의 최근 대화 내용입니다. 이 내용을 바탕으로
1. 중심 주제를 하나로 요약하고
2. 사용자의 감정 흐름을 한 줄로 설명하고
3. 마지막으로 한 문장 통찰을 생성하세요.

### 대화 내용 ###
{chr(10).join(f"- {d}" for d in dialogues)}
'''

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ GPT 요약 실패: {str(e)}"


if __name__ == "__main__":
    sample_dialogue = [
        "삶의 의미를 찾고 싶어요.",
        "가끔 무기력해요.",
        "다시 시작하고 싶어요.",
        "나는 누구인지 고민돼요.",
        "자연을 보면 마음이 차분해져요.",
        "계획을 세우고 실행하고 싶어요."
    ]

    summary = summarize_dialogue(sample_dialogue)
