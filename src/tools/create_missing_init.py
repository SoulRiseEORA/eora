"""
apply_eora_memory_patches.py
────────────────────────────
이 스크립트를 실행하면 다음 네 모듈이 자동 패치됩니다.

1. memory_db_mongo.py
   * Redis 재연결 루프 + 캐시 실패 안전 처리

2. emotion_system_full_integrator.py
   * 2값/3값 언팩 대응
   * summary_prompt / timestamp 보정 코드 추가

3. refined_recall_filter.py
   * clean_recall_list() 강화 (빈 summary/timestamp 필터링)

4. real_time_recall_validator.py
   * quick_dry_run() 자체 테스트 함수 추가

원본 코드 삭제 없이 필요한 구문을 삽입합니다.
"""

import os, re, sys, datetime, textwrap

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def patch_file(path, pattern, insert_code, anchor="after"):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    if insert_code.strip() in src:
        return False  # already patched
    m = re.search(pattern, src, re.MULTILINE)
    if not m:
        print("⚠️ 패턴을 못 찾음:", path)
        return False
    idx = m.end() if anchor == "after" else m.start()
    dst = src[:idx] + "\n" + insert_code.rstrip() + "\n" + src[idx:]
    backup = path + ".bak"
    if not os.path.isfile(backup):
        with open(backup, "w", encoding="utf-8") as b:
            b.write(src)
    with open(path, "w", encoding="utf-8") as f:
        f.write(dst)
    print("✅ Patched:", os.path.relpath(path, SRC))
    return True

def main():
    # 1) memory_db_mongo.py
    mem_db = os.path.join(SRC, "eora_memory", "memory_db_mongo.py")
    if os.path.isfile(mem_db):
        patch_file(
            mem_db,
            r"import\s+redis",
            textwrap.dedent("""                # Redis 재연결 루프 (자동 추가)
                REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                for _ in range(5):
                    try:
                        r = redis.from_url(REDIS_URL, socket_timeout=2)
                        r.ping()
                        break
                    except redis.RedisError as e:
                        print("⚠️ Redis 재연결 시도:", e)
                        import time; time.sleep(1)
                else:
                    r = None
            """)
        )

        patch_file(
            mem_db,
            r"def\s+cache_set",
            textwrap.dedent("""                if r is None:
                    return    # 캐시 미사용
            """),
            anchor="after"
        )

    # 2) emotion_system_full_integrator.py
    integrator = os.path.join(SRC, "eora_memory", "emotion_system_full_integrator.py")
    if os.path.isfile(integrator):
        patch_file(
            integrator,
            r"tmp\s*=\s*estimate_emotion",
            textwrap.dedent("""                if len(tmp) == 3:
                    emo_label, emo_code, emo_score = tmp
                else:
                    emo_label, emo_score = tmp
                    from emotion_system.memory_structurer_advanced_emotion_code import EMOTION_CODE_MAP
                    emo_code = EMOTION_CODE_MAP.get(emo_label, {}).get("code", "EXXX")
            """)
        )
        patch_file(
            integrator,
            r"memory\.update\(",
            textwrap.dedent("""                # 보정: summary_prompt, timestamp 비어 있으면 기본값
                if not memory.get("summary_prompt", "").strip():
                    memory["summary_prompt"] = (memory.get("gpt_response") or "…")[:120]
                if not memory.get("timestamp"):
                    memory["timestamp"] = datetime.datetime.utcnow().isoformat()
            """)
        )

    # 3) refined_recall_filter.py
    recall_filter = os.path.join(SRC, "eora_memory", "refined_recall_filter.py")
    if os.path.isfile(recall_filter):
        patch_file(
            recall_filter,
            r"def\s+clean_recall_list",
            textwrap.dedent("""                # 빈 summary 혹은 timestamp 제거
                recalls = [m for m in recalls if m.get("summary_prompt") and m.get("timestamp")]
            """),
            anchor="after"
        )

    # 4) real_time_recall_validator.py
    validator = os.path.join(SRC, "eora_memory", "real_time_recall_validator.py")
    if os.path.isfile(validator):
        patch_file(
            validator,
            r"def\s+validate_recall",
            textwrap.dedent("""                def quick_dry_run():
                    sample = {"summary_prompt":"테스트","timestamp":"2025-01-01T00:00"}
                    assert validate_recall("테스트", sample)
                    print("✅ 회상 검증 통과")
            """)
        )

if __name__ == "__main__":
    main()