from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Dict, Any, List
import asyncio

from EORA.file_extractor import extract_text_from_file
from memory_db import save_chunk
from EORA.gpt_router import ask

logger = logging.getLogger(__name__)

class EORABackend:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.app = FastAPI()
            self._setup_routes()
            self._initialized = True
    
    def _setup_routes(self):
        """라우트 설정"""
        @self.app.post("/upload")
        async def upload_file(file: UploadFile, prompt: str = Form(...)):
            try:
                file_text = extract_text_from_file(file)
                if file_text.startswith("[파일 추출 오류]") or "지원되지 않는 파일 형식" in file_text:
                    return JSONResponse(content={"error": file_text}, status_code=400)
            except Exception as e:
                return JSONResponse(content={"error": f"파일 처리 실패: {str(e)}"}, status_code=500)

            # 청크 처리
            lines = file_text.splitlines()
            chunks = []
            buffer = ""
            for line in lines:
                if len(buffer) + len(line) < 1500:
                    buffer += line + "\n"
                else:
                    chunks.append(buffer)
                    buffer = line + "\n"
            if buffer:
                chunks.append(buffer)

            results = []
            for i, chunk in enumerate(chunks):
                save_chunk("최근시스템기억", chunk.strip())
                enhanced_prompt = f"[분석된 첨부파일 청크 {i+1}]\n{chunk}\n\n[질문]\n{prompt}"
                reply = ask(prompt=enhanced_prompt, system_msg="분석 내용을 반영하여 응답하세요.", max_tokens=512)
                results.append({"청크": i + 1, "응답": reply})

            return {"응답결과": results, "청크수": len(chunks)}
    
    async def process_input(self, text: str) -> Dict[str, Any]:
        """입력 처리"""
        try:
            # 기본 처리
            result = {
                "text": text,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "success"
            }
            
            # 추가 처리 로직
            # TODO: 실제 처리 로직 구현
            
            return result
            
        except Exception as e:
            logger.error(f"입력 처리 실패: {str(e)}")
            return {
                "text": text,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "error",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """상태 확인"""
        return {
            "status": "running",
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def run(self, host: str = "127.0.0.1", port: int = 8600):
        """서버 실행"""
        uvicorn.run(self.app, host=host, port=port)

if __name__ == "__main__":
    backend = EORABackend()
    backend.run()
