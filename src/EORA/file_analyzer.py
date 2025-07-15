
import os
from memory_db import save_chunk

def split_by_lines(text: str, lines_per_chunk: int = 20):
    lines = text.splitlines()
    return ["\n".join(lines[i:i+lines_per_chunk]) for i in range(0, len(lines), lines_per_chunk)]

def is_conversation_chunk(chunk: str) -> bool:
    return "사용자:" in chunk and "GPT:" in chunk

def analyze_file(file_path: str, category: str = "파일분석") -> str:
    if not os.path.exists(file_path):
        return "[파일 없음] 경로가 존재하지 않습니다."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "사용자:" in content and "GPT:" in content:
            chunks = split_by_lines(content, 30)
            for chunk in chunks:
                if is_conversation_chunk(chunk):
                    save_chunk("GPT_대화분석", chunk)
                    save_chunk("최근시스템기억", chunk)
            return "[분석 완료] GPT 대화 분리 및 system_prompt 반영 완료"

        chunks = split_by_lines(content, 30)
        for chunk in chunks:
            save_chunk(category, chunk.strip())
            save_chunk("최근시스템기억", chunk.strip())

        return f"[분석 완료] {os.path.basename(file_path)} / {len(chunks)}개의 청크 저장됨 (system_prompt 포함)"

    except Exception as e:
        return f"[분석 오류] {str(e)}"
