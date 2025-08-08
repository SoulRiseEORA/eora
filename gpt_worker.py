"""
gpt_worker.py
- GPT 작업자 스레드 구현
"""

import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any
from PyQt5.QtCore import QThread, pyqtSignal
from aura_system.ai_chat import get_eora_ai
from aura_system.memory_manager import get_memory_manager
from aura_system.vector_store import get_embedding
from is_rejection_function import is_rejection

logger = logging.getLogger(__name__)

class GPTWorker(QThread):
    """GPT 작업자 스레드"""
    response_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, user_input: str, system_message: Optional[str] = None):
        print("[GPTWorker.__init__] 진입", user_input)
        super().__init__()
        self.user_input = user_input
        self.system_message = system_message
        self.loop = None
        self.memory_manager = None  # run()에서 생성
        
    def run(self):
        """작업 실행"""
        print("[GPTWorker.run] 진입")
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            print("[GPTWorker.run] 이벤트 루프 생성 완료")
            # 반드시 QThread 루프에서 get_memory_manager() 호출
            self.memory_manager = self.loop.run_until_complete(get_memory_manager())
            response = self.loop.run_until_complete(self.process_message())
            if not isinstance(response, dict) or response is None:
                print("[GPTWorker.run] 경고: response가 dict가 아님 또는 None!", type(response), response)
                response = {"response": str(response) if response is not None else "응답 없음"}
            self.response_ready.emit(response)
            print("[GPTWorker.run] emit 완료")
        except Exception as e:
            print("[GPTWorker.run] 예외:", e)
            logger.error(f"⚠️ 메시지 처리 실패: {str(e)}")
            self.error_occurred.emit(str(e))
        finally:
            if self.loop:
                self.loop.close()
            print("[GPTWorker.run] 루프 종료")
            
    async def process_message(self) -> dict:
        """메시지 처리"""
        try:
            print("[GPTWorker.process_message] 진입")
            eora = await get_eora_ai()
            
            # 임베딩 캐싱 시스템
            import hashlib
            input_hash = hashlib.md5(self.user_input.encode()).hexdigest()
            if not hasattr(self, '_embedding_cache'):
                self._embedding_cache = {}
            
            if input_hash in self._embedding_cache:
                input_embedding = self._embedding_cache[input_hash]
                print("[GPTWorker.process_message] 임베딩 캐시 히트")
            else:
                input_embedding = get_embedding(self.user_input)
                self._embedding_cache[input_hash] = input_embedding
                # 캐시 크기 제한 (최대 100개)
                if len(self._embedding_cache) > 100:
                    oldest_key = next(iter(self._embedding_cache))
                    del self._embedding_cache[oldest_key]
                print("[GPTWorker.process_message] 임베딩 생성 완료")
            try:
                memories = await asyncio.wait_for(
                    self.memory_manager.recall_memory(self.user_input),
                    timeout=2  # 타임아웃 단축 (5초 → 2초)
                )
            except asyncio.TimeoutError:
                print("[GPTWorker.process_message] 메모리 recall 타임아웃 (2초)")
                memories = []
            print("[GPTWorker.process_message] 메모리 recall 완료")
            try:
                response = await asyncio.wait_for(
                    eora.respond_async(
                        user_input=self.user_input,
                        system_message=self.system_message,
                        memories=memories
                    ),
                    timeout=12  # 타임아웃 단축 (15초 → 12초)
                )
                if response is None:
                    print("[GPTWorker.process_message] respond_async가 None 반환")
                    response = {"response": "AI 응답이 없습니다."}
            except asyncio.TimeoutError:
                print("[GPTWorker.process_message] respond_async 타임아웃")
                response = {"response": "AI 응답이 지연되고 있습니다."}
            print("[GPTWorker.process_message] respond_async 완료")
            await self.memory_manager.store_memory(
                content=self.user_input,
                metadata={
                    "type": "user_input",
                    "timestamp": asyncio.get_event_loop().time()
                },
                embedding=input_embedding
            )
            print("[GPTWorker.process_message] 메모리 저장 완료")
            return response
        except Exception as e:
            print("[GPTWorker.process_message] 예외:", e)
            logger.error(f"⚠️ 메시지 처리 실패: {str(e)}")
            return {"response": f"오류: {str(e)}"}
