import asyncio
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class InsightAnalyzer:
    async def analyze(self, text: str) -> str:
        """통찰 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 분석 결과
        """
        try:
            client = OpenAI()
            
            # 동기 함수를 비동기로 실행
            def analyze_insight():
                try:
                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": "다음 텍스트에서 중요한 통찰이나 패턴을 찾아주세요."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"⚠️ 통찰 분석 실패: {str(e)}")
                    return None
                
            return await asyncio.to_thread(analyze_insight)
        except Exception as e:
            logger.error(f"⚠️ 통찰 분석 실패: {str(e)}")
            return None 