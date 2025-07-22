"""
fix_prompts_updated.py
- Locates ai_prompts.json in src/ai_brain first, then in parent ai_brain.
- Cleans trailing commas and control chars, reformats JSON.
- Restores from .bak if present.
- Place this in src folder and run: python fix_prompts_updated.py
"""

import os
import json
import re
import shutil
import sys

def find_json_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Search order: src/ai_brain, parent/ai_brain
    candidates = [
        os.path.join(script_dir, "ai_brain", "ai_prompts.json"),
        os.path.join(os.path.dirname(script_dir), "ai_brain", "ai_prompts.json")
    ]
    for path in candidates:
        if os.path.exists(path):
            bak = path + ".bak"
            return path, bak
    return None, None

def main():
    json_path, backup_path = find_json_path()
    if not json_path:
        print("❌ ai_prompts.json을 찾을 수 없습니다. src/ai_brain 또는 상위 ai_brain 폴더를 확인하세요.")
        sys.exit(1)
    print(f"🔍 JSON 파일 위치: {json_path}")

    # Restore from backup if exists
    if backup_path and os.path.exists(backup_path):
        try:
            shutil.copy(backup_path, json_path)
            print(f"✅ 백업에서 복원 완료: {backup_path}")
        except Exception as e:
            print(f"⚠️ 백업 복원 실패: {e}")

    # Read file
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {e}")
        sys.exit(1)

    # Clean trailing commas
    text = re.sub(r',\s*([\]\}])', r'\1', text)
    # Replace control chars
    text = re.sub(r'[\x00-\x1f]', ' ', text)

    # Parse JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {e}")
        sys.exit(1)

    # Write back formatted
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ JSON 전처리 및 포맷팅 완료")
    except Exception as e:
        print(f"❌ JSON 저장 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()