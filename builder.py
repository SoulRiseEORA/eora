
# builder.py

class ExecutableBuilder:
    """
    실행 가능한 파일 (.exe, .app 등)을 생성하는 빌더 클래스
    향후 PyInstaller, zipapp, cx_Freeze 등을 연동 가능
    """

    def build_executable(self, source_folder="src", output_name="AI_AutoTool.exe"):
        print(f"🛠 실행파일 생성 시뮬레이션: {source_folder} → {output_name}")
        # 실제 빌드 로직은 pyinstaller 명령 실행 또는 zipapp 생성 방식으로 확장 가능
        return f"{output_name} 생성 완료 (시뮬레이션)"
