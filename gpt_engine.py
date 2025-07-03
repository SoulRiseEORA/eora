import openai
import asyncio

openai.api_key = "your-api-key"

async def get_openai_chat_response(prompt, model="gpt-3.5-turbo", system_msg=""):
    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": system_msg or "당신은 진화형 AI EORA입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[GPT 호출 오류] {str(e)}"

async def get_streaming_response(prompt, model="gpt-3.5-turbo", system_msg=""):
    try:
        stream = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": system_msg or "당신은 진화형 AI EORA입니다."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        async for chunk in stream:
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]
    except Exception as e:
        yield f"[GPT 스트리밍 오류] {str(e)}"

def do_task(prompt: str, model="gpt-3.5-turbo", system_message=""):
    return asyncio.run(get_openai_chat_response(prompt, model=model, system_msg=system_message))