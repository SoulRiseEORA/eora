
import os

def create_project_structure(project_name: str, base_dir: str = "projects"):
    project_path = os.path.join(base_dir, project_name)
    os.makedirs(project_path, exist_ok=True)

    folders = ["docs", "src", "tests", "ui"]
    for folder in folders:
        os.makedirs(os.path.join(project_path, folder), exist_ok=True)

    with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n\n이 프로젝트는 금강GPT로 자동 생성되었습니다.\n")

    return project_path
