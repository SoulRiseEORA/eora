
import os
import mimetypes
import fitz  # PyMuPDF
from ebooklib import epub

class FileProcessor:
    def __init__(self):
        pass

    def get_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"[텍스트 파일 읽기 오류] {str(e)}"

    def get_pdf_text(self, file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            return f"[PDF 처리 오류] {str(e)}"

    def get_epub_text(self, file_path: str) -> str:
        try:
            book = epub.read_epub(file_path)
            text = ""
            for item in book.get_items():
                if item.get_type() == epub.ITEM_DOCUMENT:
                    text += item.get_content().decode("utf-8")
            return text
        except Exception as e:
            return f"[EPUB 처리 오류] {str(e)}"

    def split_large_text(self, text: str, max_tokens: int = 8192) -> list:
        chunk_size = max_tokens * 4
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def process_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return "❌ 파일이 존재하지 않습니다."

        mime_type, _ = mimetypes.guess_type(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext.endswith(".pdf"):
                return self.get_pdf_text(file_path)
            elif ext.endswith(".epub"):
                return self.get_epub_text(file_path)
            elif mime_type and mime_type.startswith("text"):
                return self.get_file_content(file_path)
            elif mime_type and mime_type.startswith("image"):
                return "[🖼 이미지 파일] 분석 준비 중..."
            elif mime_type and mime_type.startswith("audio"):
                return "[🔊 음성 파일] 음성 인식 및 텍스트 변환 예정"
            elif mime_type and mime_type.startswith("video"):
                return "[🎥 영상 파일] 프레임 분석 및 요약 예정"
            else:
                return "[⚠️ 지원되지 않는 파일 형식]"
        except Exception as e:
            return f"[파일 분석 오류] {str(e)}"

    def analyze_file(self, file_path: str) -> str:
        content = self.process_file(file_path)
        if len(content) > 1500:
            return content[:1500] + "\n... (생략됨)"
        return content
