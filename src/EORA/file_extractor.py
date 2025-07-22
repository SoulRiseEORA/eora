import os

def extract_text_from_file(file_path: str) -> list[str]:
    ext = os.path.splitext(file_path)[1].lower()
    chunks = []

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                chunks = split_to_chunks(text)

        elif ext == ".docx":
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            chunks = split_to_chunks(text)

        elif ext == ".pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            chunks = split_to_chunks(text)

        elif ext == ".hwp":
            import olefile
            ole = olefile.OleFileIO(file_path)
            text = ole.openstream("PrvText").read().decode("utf-16")
            chunks = split_to_chunks(text)

        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                for item in data:
                    user = item.get("user", "")
                    reply = item.get("reply", "")
                    chunks.append(f"👤 {user}\n🤖 {reply}")
        else:
            chunks = ["❌ 지원되지 않는 파일 형식입니다."]
    except Exception as e:
        chunks = [f"❌ 추출 실패: {str(e)}"]

    return chunks

def split_to_chunks(text: str, size=1000) -> list[str]:
    return [text[i:i+size] for i in range(0, len(text), size)]