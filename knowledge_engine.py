# src/knowledge_engine.py

import json
import os
import re
from collections import defaultdict
from typing import List

# 가정: gpts지침.txt와 파이썬교재.xlsx 파싱 결과는 아래 경로에 JSON으로 존재한다고 가정
GPTS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "data/gpts_index.json")
PYTHON_FUNCS_PATH = os.path.join(os.path.dirname(__file__), "data/python_functions.json")

from suggest_python_fix import suggest_python_fix
from suggest_gpts_guidelines import suggest_gpts_guidelines
class KnowledgeEngine:
    def __init__(self):
        self.gpts_index = {}
        self.python_funcs = {}
        self.error_history = defaultdict(int)  # 반복 에러 감지용

        self._load_data()

    def _load_data(self):
        if os.path.exists(GPTS_INDEX_PATH):
            with open(GPTS_INDEX_PATH, "r", encoding="utf-8") as f:
                self.gpts_index = json.load(f)

        if os.path.exists(PYTHON_FUNCS_PATH):
            with open(PYTHON_FUNCS_PATH, "r", encoding="utf-8") as f:
                self.python_funcs = json.load(f)

    def suggest_gpts_guidelines(self, phase: str, keyword: str = "") -> List[str]:
        """
        단계별(generation, error_fix, planning 등) 지침 필터링
        """
        suggestions = []
        for item in self.gpts_index.get(phase, []):
            if keyword.lower() in item["title"].lower() or keyword.lower() in item["description"].lower():
                suggestions.append(f"{item['title']}: {item['description']}")
        return suggestions[:5]

    def suggest_python_fix(self, error_msg: str) -> List[str]:
        """
        에러 메시지를 기반으로 파이썬 문법/함수/해결책 제공
        """
        matches = []
        for key, info in self.python_funcs.items():
            if re.search(key, error_msg, re.IGNORECASE):
                matches.append(f"{key} 관련 함수: {info['func']} → {info['tip']}")
        return matches[:5]

    def track_error(self, error_key: str) -> str:
        """
        동일한 에러 2~3회 이상 발생 시 경고/대안 제시
        """
        self.error_history[error_key] += 1
        count = self.error_history[error_key]

        if count == 2:
            return f"[⚠] 동일한 오류가 2회 발생했습니다. GPT 지침/문법을 재검토합니다."
        elif count >= 3:
            return f"[🚨] 3회 이상 반복 오류 → 웹 검색 또는 사용자 조치가 필요합니다."
        return ""

    def quick_lookup(self, term: str) -> str:
        """
        빠른 개념 조회
        """
        for key, info in self.python_funcs.items():
            if term.lower() in key.lower():
                return f"{info['func']} → {info['tip']}"
        return "일치하는 문법/개념이 없습니다."


    def suggest_gpts_guidelines(self, phase: str, keyword: str = ''):
        return suggest_gpts_guidelines(phase, keyword)
