
import os
import json
import pandas as pd

def extract_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[-1].lower()

    try:
        if ext in [".txt", ".py", ".md"]:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        elif ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)

        elif ext == ".csv":
            df = pd.read_csv(path)
            return df.to_string(index=False)

        elif ext == ".docx":
            from docx import Document
            doc = Document(path)
            return "\n".join([para.text for para in doc.paragraphs])

        elif ext == ".pdf":
            import fitz  # PyMuPDF
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text

        elif ext in [".mp3", ".wav"]:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(path)
            return result.get("text", "")

        else:
            return f"[지원하지 않는 파일 형식입니다: {ext}]"

    except Exception as e:
        return f"[파일 분석 실패: {str(e)}]"
