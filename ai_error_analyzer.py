
# ai_error_analyzer.py

import traceback
from datetime import datetime
import os

class AIErrorAnalyzer:
    def __init__(self):
        self.log_path = "logs/error_notes.md"
        os.makedirs("logs", exist_ok=True)

    def analyze_code(self, code: str) -> str:
        try:
            compile(code, "<string>", "exec")
            return "✅ Syntax OK"
        except SyntaxError as e:
            msg = f"❌ SyntaxError: {e.msg} at line {e.lineno}"
            self._log_error("SyntaxError", code, suggestion="괄호, 들여쓰기, 문자열 닫힘 확인")
            return msg
        except IndentationError as e:
            msg = f"❌ IndentationError: {e.msg} at line {e.lineno}"
            self._log_error("IndentationError", code, suggestion="탭/공백 혼용 또는 블록 누락")
            return msg
        except Exception as e:
            err_type = type(e).__name__
            msg = f"❌ {err_type}: {e}"
            self._log_error(err_type, code)
            return msg

    def _log_error(self, error_type, code, suggestion=""):
        with open(self.log_path, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"## 🧾 오류 기록 ({now})\n")
            f.write(f"- 오류 종류: {error_type}\n")
            f.write(f"- 코드 스니펫:\n```python\n{code.strip()[:300]}\n```\n")
            if suggestion:
                f.write(f"- GPT 제안: {suggestion}\n")
            f.write(f"- 참고 링크: https://stackoverflow.com/search?q={error_type.replace(' ', '+')}\n\n")
