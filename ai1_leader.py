from ai_auto_backup_manager import rollback_to_last_success
from ai_architect import AIArchitect
from ai_ui_designer import AIUIDesigner
from ai_code_generator import AICodeGenerator
from ai_error_analyzer import AIErrorAnalyzer
from ai_optimizer import AIOptimizer
from builder import ExecutableBuilder
from ai_web_macro_agent_ddgs_safe import AIWebMacroAgent
from knowledge_engine import KnowledgeEngine
from error_notebook import ErrorNotebook
from web_search_solution import web_search_solution
from project_initializer import create_project_structure
from log_panel import LogPanel
from web_searcher import web_search_solution
from error_notebook import ErrorNotebook
from ai_chat import get_eora_instance
import time
import os

class AutoMacro:
    def __init__(self, project_name: str, log_panel=None):
        if not os.path.exists('projects/KumgangGPT'):
            create_project_structure('KumgangGPT')
        self.project = project_name
        self.log = log_panel or print

        self.architect = AIArchitect()
        self.designer = AIUIDesigner()
        self.generator = AICodeGenerator()
        self.analyzer = AIErrorAnalyzer()
        self.optimizer = AIOptimizer()
        self.builder = ExecutableBuilder()
        self.web_agent = AIWebMacroAgent()
        self.leader = AI1Leader()
        self.error_note = ErrorNotebook()
        self.eora = get_eora_instance()

    def start_auto_production(self, user_need: str):
        self._log("🚀 자동 제작을 시작합니다.")

        self._log("🧠 기획 분석 중...")
        plan = self.architect.plan_project_from_text(user_need)
        time.sleep(1)

        self._log("🖌 UI 설계 생성 중...")
        ui_structure = self.designer.create_ui_layout(plan)
        time.sleep(1)

        # ✅ 이오라에게 자동 진화 감지 전달
        self.eora.monitor_any(f"[기획 내용]\n{plan}\n[UI 설계]\n{ui_structure}")

        self._log("📁 프로젝트 디렉토리 생성 중...")
        create_project_structure(plan)

        self._log("⚙️ 코드 생성 중...")
        modules = self.generator.generate_modules(plan)
        time.sleep(1)

        self._log("🧪 코드 실행 및 오류 분석 중...")
        error_msg = ""
        for i in range(6):
            if self.analyzer.analyze_and_fix():
                self._log(f"✅ 오류 수정 완료 (시도 {i+1})")
                if error_msg:
                    self.error_note.save_error(error_msg)
                break
            else:
                error_msg = self.analyzer.get_last_error_message()
                self._log(f"❌ 오류 계속 발생 (시도 {i+1})")
                if i >= 2:
                    self._log("🧠 브레인스토밍 시작")
                    brainstorm = self.leader.brainstorm_if_blocked(error_msg)
                    self._log(brainstorm)
                    self.eora.monitor_any(f"[오류 인식]\n{error_msg}\n[브레인스토밍 결과]\n{brainstorm}")
                if i >= 3:
                    tip = suggest_python_fix(error_msg)
                    self._log(f"📘 교재 참고: {tip}")
                if i >= 4:
                    web = web_search_solution(error_msg)
                    self._log(f"🌐 웹 검색 결과: {web}")
                if i >= 5:
                    note = self.error_note.lookup_error(error_msg)
                    self._log(f"📓 에러노트 참고: {note}")
            time.sleep(1)

        self._log("⚡ 성능 최적화 진행 중...")
        self.optimizer.optimize()

        self._log("🔍 필수 도구 설치 확인 중...")
        missing = ["pyinstaller"]
        for tool in missing:
            self._log(f"❗ 필요한 도구 발견: {tool} → 설치 시도")
            self.web_agent.install_tool(tool)

        self._log("🛠 실행파일 빌드 중...")
        self.builder.build_executable()

        self._log("🎉 전체 자동제작이 완료되었습니다!")

    def _log(self, msg):
        if callable(self.log):
            self.log(msg)
        elif hasattr(self.log, "add_log"):
            self.log.add_log(msg, "system")