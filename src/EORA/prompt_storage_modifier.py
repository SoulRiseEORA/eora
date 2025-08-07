import os
import json
import shutil
import re
from pathlib import Path

# ✅ 시스템 프롬프트 저장소 위치
BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = Path(__file__).resolve().parent.parent / "ai_brain" / "ai_prompts.json"
BACKUP_PATH = PROMPT_PATH.with_suffix(".bak")

# ✅ In-memory last known good data
_last_prompt_cache = None

# ✅ 현재 등록된 프롬프트 불러오기 (복구 구조 포함)
def load_prompts():
    global _last_prompt_cache
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _last_prompt_cache = data
        # ✅ 리스트 항목을 문자열로 병합 (UI에 표시되도록)
        # → 실제 저장 구조가 리스트가 아닌 문자열로 변질되는 문제 방지 위해 아래 코드 주석처리
        # for ai_key, value in data.items():
        #     for key, field in value.items():
        #         if isinstance(field, list):
        #             data[ai_key][key] = "\n".join(field)
        return data
    except json.JSONDecodeError as e:
        print(f"❌ JSONDecodeError at char {e.pos}: {e.msg}")
        if BACKUP_PATH.exists():
            try:
                with open(BACKUP_PATH, "r", encoding="utf-8") as fb:
                    data = json.load(fb)
                print("✅ Backup JSON loaded successfully.")
                _last_prompt_cache = data
                return data
            except Exception as be:
                print(f"❌ Backup JSON also invalid: {be}")
        if _last_prompt_cache is not None:
            print("⚠️ Returning last known good prompts from cache.")
            return _last_prompt_cache
        print("⚠️ No valid JSON found. Returning empty data.")
        return {}
    except FileNotFoundError:
        print("⚠️ prompt_storage.json not found. Returning empty data.")
        return _last_prompt_cache or {}

# ✅ 추가 문장 정제
def clean_addition(addition: str) -> str:
    match = re.search(r'"([^"]+)"', addition)
    if match:
        return match.group(1).strip()
    parts = re.split(r'(저장|추가|기억|기록|알아둬|보존|반영|등록).*$' , addition)
    return parts[0].strip()

# ✅ 특정 키에 해당하는 프롬프트 업데이트
def update_ai1_prompt(section: str, addition: str):
    data = load_prompts()
    if not isinstance(data, dict):
        data = {}

    if "ai1" not in data or not isinstance(data["ai1"], dict):
        data["ai1"] = {}

    sec_data = data["ai1"].get(section)
    # 항상 리스트로 변환
    if isinstance(sec_data, str):
        lst = [sec_data]
    elif isinstance(sec_data, list):
        lst = sec_data
    else:
        lst = []

    clean_text = clean_addition(addition)
    # 빈 문자열이면 원본 사용 (최후의 방어)
    if not clean_text:
        clean_text = addition.strip()
    if clean_text and clean_text not in lst:
        lst.append(clean_text)
        print(f"✅ 프롬프트 저장: {clean_text}")
    data["ai1"][section] = lst

    # ✅ 백업 및 저장
    try:
        if PROMPT_PATH.exists():
            shutil.copy(PROMPT_PATH, BACKUP_PATH)
        with open(PROMPT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        global _last_prompt_cache
        _last_prompt_cache = data
        print(f"✅ 실제 저장됨: {PROMPT_PATH}")
        return True, "✅ 저장 성공"
    except Exception as e:
        print(f"❌ 저장 실패: {e} (경로: {PROMPT_PATH})")
        return False, f"❌ 저장 실패: {e}"

# ✅ 저장된 프롬프트 항목 제거
def remove_prompt(section: str):
    data = load_prompts()
    if "ai1" in data and section in data["ai1"]:
        del data["ai1"][section]
        try:
            with open(PROMPT_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"🗑️ 프롬프트 '{section}' 항목이 제거되었습니다.")
            return True
        except Exception as e:
            print(f"⚠️ 제거 실패: {e}")
    return False

# ✅ 사용자 입력에서 '프롬프트로 저장' 명령을 감지해 실제로 저장하는 함수
def handle_prompt_save_command(user_input: str):
    """
    사용자가 '프롬프트로 저장' 명령을 입력하면 따옴표 안의 문장을 추출해 실제로 저장합니다.
    예: '"대화중 판단이 필요 할때는 직감 시스템을 이용합니다."프롬프트로 저장하세요.'
    """
    if "프롬프트로 저장" in user_input:
        match = re.search(r'"([^"]+)"', user_input)
        if match:
            prompt_text = match.group(1).strip()
            print(f"[프롬프트 저장 명령 감지] 추출된 문장: {prompt_text}")
            ok, msg = update_ai1_prompt('system', prompt_text)
            print(f"[프롬프트 저장 결과] {msg}")
            return True, msg
        else:
            print("[프롬프트 저장 명령 감지] 따옴표 안 문장 추출 실패")
            return False, "❌ 따옴표 안에 저장할 문장을 정확히 입력하세요."
    return False, "프롬프트 저장 명령이 아닙니다."

if __name__ == "__main__":
    print("[프롬프트 저장 테스트 모드]")
    while True:
        user_input = input("명령을 입력하세요(종료: exit): ")
        if user_input.strip().lower() == "exit":
            print("종료합니다.")
            break
        ok, msg = handle_prompt_save_command(user_input)
        print(f"[실행 결과] {msg}")
