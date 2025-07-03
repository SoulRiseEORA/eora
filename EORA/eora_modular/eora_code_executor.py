def extract_python_code(gpt_text):
    if "```python" in gpt_text:
        try:
            return gpt_text.split("```python")[1].split("```")[0].strip()
        except:
            return None
    return None

def run_python_code(code):
    import subprocess
    try:
        with open("temp_code.py", "w", encoding="utf-8") as f:
            f.write(code)
        out = subprocess.check_output(["python", "temp_code.py"], stderr=subprocess.STDOUT, timeout=5)
        return out.decode("utf-8")
    except Exception as e:
        return f"❌ 실행 실패: {e}"
