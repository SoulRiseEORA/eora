"""
EORA 전체 프로젝트에서 잘못된 import 경로 자동 수정기
- from XXX import YYY → 실제 위치 기준으로 교정
"""

import os
import re

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
MODULE_ROOT = BASE_PATH  # src 폴더

# 모든 .py 파일 경로 수집
def find_all_python_files():
    paths = []
    for root, dirs, files in os.walk(MODULE_ROOT):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                paths.append(full_path)
    return paths

# 모듈 경로 인덱스 생성
def build_module_map():
    module_map = {}
    for file_path in find_all_python_files():
        rel_path = os.path.relpath(file_path, MODULE_ROOT).replace("\\", "/").replace("/", ".")
        if rel_path.endswith(".py"):
            module = rel_path[:-3]  # remove .py
            name = os.path.basename(module)
            module_map[name] = module
    return module_map

# import 구문 수정
def correct_imports(file_path, module_map):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    corrected_lines = []

    for line in lines:
        match = re.match(r"from\s+([a-zA-Z0-9_]+)\s+import\s+", line)
        if match:
            module_name = match.group(1)
            if module_name in module_map:
                correct_path = module_map[module_name]
                new_line = line.replace(f"from {module_name} import", f"from {correct_path} import")
                corrected_lines.append(new_line)
                changed = True
                continue
        corrected_lines.append(line)

    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(corrected_lines)
        print(f"✅ import 경로 수정됨: {file_path}")

if __name__ == "__main__":
    module_map = build_module_map()
    for py_file in find_all_python_files():
        correct_imports(py_file, module_map)

    print("🎯 모든 파일의 import 경로 자동 수정 완료.")
