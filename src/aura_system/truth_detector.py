import asyncio
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class TruthDetector:
    async def detect(self, text: str) -> str:
        """진실 탐지
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 분석 결과
        """
        try:
            client = OpenAI()
            
            # 동기 함수를 비동기로 실행
            def detect_truth():
                try:
                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": "다음 텍스트의 진실성을 분석해주세요. 사실, 의견, 추측 등을 구분해주세요."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"⚠️ 진실 탐지 실패: {str(e)}")
                    return None
                
            return await asyncio.to_thread(detect_truth)
        except Exception as e:
            logger.error(f"⚠️ 진실 탐지 실패: {str(e)}")
            return None 