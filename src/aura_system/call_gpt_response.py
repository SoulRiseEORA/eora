import asyncio
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

async def call_gpt_response(user_input: str, system_message: str = "") -> str:
    """GPT 응답 생성
    
    Args:
        user_input (str): 사용자 입력
        system_message (str, optional): 시스템 메시지
        
    Returns:
        str: GPT 응답
    """
    try:
        client = OpenAI()
        
        # 동기 함수를 비동기로 실행
        def generate_response():
            try:
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_message} if system_message else None,
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"⚠️ GPT 응답 생성 실패: {str(e)}")
                return None
                
        return await asyncio.to_thread(generate_response)
    except Exception as e:
        logger.error(f"⚠️ GPT 응답 생성 실패: {str(e)}")
        return None 