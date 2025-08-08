import ast
import sys

REQUIRED_WIDGETS = {
    "file_panel": ["tree", "code_view", "log_view"],
    "session_panel": ["session_list", "btn_add", "btn_del"],
    "splitter": ["file_panel", "session_panel", "tabs"],
    "setCentralWidget": ["splitter"]
}

TEMPLATE_INSERT = {
"file_panel": """        self.tree = QTreeView()"
        self.tree_model = QFileSystemModel()
        self.tree_model.setRootPath("C:/")
        self.tree.setModel(self.tree_model)
        self.tree.setRootIndex(self.tree_model.index("C:/"))
        self.tree.setColumnWidth(0, 250)

        self.code_view = QTextEdit("💻 코드 보기")
        self.log_view = QTextEdit("📜 로그")
        self.log_view.setReadOnly(True)
""","
"session_panel": """        self.session_list = QListWidget()"
        self.btn_add = QPushButton("➕ 세션 추가")
        self.btn_del = QPushButton("➖ 세션 삭제")
""","
"splitter": """        splitter = QSplitter(Qt.Horizontal)"
        splitter.addWidget(file_panel)
        splitter.addWidget(session_panel)
        splitter.addWidget(self.tabs)
""","
"setCentralWidget": """        container = QWidget()"
        layout = QVBoxLayout(container)
        layout.addWidget(splitter)
        self.setCentralWidget(container)
""""
}

def extract_widget_names(tree):
    assigned = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned.add(target.id)
    return assigned

def extract_method_calls(tree):
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                calls.add(f"{getattr(node.func.value, 'id', '')}.{node.func.attr}")
    return calls

def check_ui_structure(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    assigned_vars = extract_widget_names(tree)
    method_calls = extract_method_calls(tree)

    print(f"🧠 GPTMainWindow 구조 점검 결과 ({filepath}):")
    all_ok = True
    missing = {}
    for section, widgets in REQUIRED_WIDGETS.items():
        print(f"🔹 {section}:")
        for w in widgets:
            var_ok = w in assigned_vars
            call_ok = any(w in call for call in method_calls)
            if not (var_ok or call_ok):
                print(f"   ❌ 누락됨: {w}")
                missing.setdefault(section, []).append(w)
                all_ok = False
            else:
                print(f"   ✅ 포함됨: {w}")
    return all_ok, missing

def auto_fix(filepath, missing):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    for line in lines:
        fixed_lines.append(line)
        if "def __init__(self):" in line:
fixed_lines.append("        # 🔧 구조 복구 시작"
")"
            for section in missing:
                if section in TEMPLATE_INSERT:
                    fixed_lines.append(TEMPLATE_INSERT[section] + "\n")
fixed_lines.append("        # 🔧 구조 복구 끝"
")"

    fixed_path = filepath.replace(".py", "_fixed.py")
    with open(fixed_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    print(f"💾 복구 완료 → {fixed_path}")
    return fixed_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python ui_structure_checker_with_fix.py <GPTMainWindow.py 경로>")
    else:
        file = sys.argv[1]
        all_ok, missing = check_ui_structure(file)
        if not all_ok:
            choice = input("\n⚠️ 일부 구조가 누락되어 있습니다. 자동 복구하시겠습니까? (y/n): ")
            if choice.lower().strip() == 'y':
                auto_fix(file, missing)
        else:
            print("\n🎉 구조가 완벽합니다. 수정할 사항이 없습니다.")