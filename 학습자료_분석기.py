
"""
금강GPT 학습자료 분석기
- configs/ 또는 ./ai_brain/aiN 폴더 내 워드, 엑셀, 텍스트, JSON 자료 자동 분석
- 학습 내용 → DB화 (memory_db.json)
- 각 AI에 프롬프트 5~7개 저장
- system_message_금강.txt 등 프롬프트 생성
"""

import os
import json
import hashlib

try:
    import docx
    import openpyxl
except ImportError:
    print("❗ docx/openpyxl 설치 필요")

ROOT = "./configs"
AI_FOLDER = "./ai_brain"
DB_PATH = "memory_db.json"
PROMPT_PATH = "system_message_금강.txt"
AI_PROMPT_DB = "ai_prompts.json"

def flatten_json(obj, prefix=""):
    result = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            result.extend(flatten_json(v, f"{prefix}{k}: "))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            result.extend(flatten_json(v, f"{prefix}[{i}] "))
    else:
        result.append(f"{prefix}{str(obj)}")
    return result

def hash_file(file):
    key = f"{file}:{os.path.getsize(file)}:{int(os.path.getmtime(file))}"
    return hashlib.md5(key.encode()).hexdigest()

def parse_file(path):
    ext = path.split(".")[-1].lower()
    results = []
    try:
        if ext == "docx":
            doc = docx.Document(path)
            results = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        elif ext == "xlsx":
            wb = openpyxl.load_workbook(path)
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    for cell in row:
                        if cell:
                            results.append(str(cell))
        elif ext == "txt":
            with open(path, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        elif ext == "json":
            with open(path, "r", encoding="utf-8") as f:
                obj = json.load(f)
                results = flatten_json(obj)
    except Exception as e:
        print(f"❌ 분석 실패: {path} - {e}")
    return results

def analyze_all(root=ROOT):
    db = {}
    seen = {}
    for base in [root, AI_FOLDER]:
        for dirpath, _, files in os.walk(base):
            for fname in files:
                if not fname.lower().endswith(("docx", "xlsx", "txt", "json")):
                    continue
                fpath = os.path.join(dirpath, fname)
                hashv = hash_file(fpath)
                if fname in seen and seen[fname] == hashv:
                    continue
                key = "금강" if "금강" in fpath else "레조나" if "레조나" in fpath else "기타"
                if key not in db:
                    db[key] = []
                parsed = parse_file(fpath)
                db[key].extend(parsed)
                seen[fname] = hashv
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
    return db

def generate_system_prompt():
    db = json.load(open(DB_PATH, encoding="utf-8"))
    lines = db.get("금강", [])[:30]
    with open(PROMPT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def extract_ai_prompts():
    prompts = {}
    for ai_n in ["ai1", "ai2", "ai3", "ai4", "ai5"]:
        path = f"{AI_FOLDER}/{ai_n}"
        prompts[ai_n] = []
        if not os.path.exists(path):
            continue
        for fname in os.listdir(path):
            if not fname.endswith((".txt", ".docx")):
                continue
            lines = parse_file(os.path.join(path, fname))
            prompts[ai_n].extend(lines[:7])
    with open(AI_PROMPT_DB, "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2)

if __name__ == "__main__":
    print("📂 금강GPT 학습자료 분석 중...")
    analyze_all()
    generate_system_prompt()
    extract_ai_prompts()
    print("✅ 학습자료 분석 + system_prompt 생성 완료")
