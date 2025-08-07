# 이 코드는 응답에서 "EORAAI" → "EORA" 로 바꿔주는 후처리 필터 예시입니다

def sanitize_response(text: str) -> str:
    return text.replace("EORAAI", "EORA")

# 사용 예시:
# 실제 GPT 응답 text 를 sanitize_response(generated_text) 로 감싸서 처리