"""
ai_manager.py
- 모든 AI 모듈을 초기화하고 GPTMainWindow 등에서 사용할 수 있도록 관리
"""

from ai_architect import analyze_requirements
from ai_ui_designer import generate_ui
from ai_code_generator import generate_code
from ai_error_analyzer import AI_ErrorAnalyzer
from ai_optimizer import AI_Optimizer

class AI_Manager:
    def __init__(self):
        self.error_ai = AI_ErrorAnalyzer()
        self.optimizer = AI_Optimizer()

    def run_architect(self, user_input):
        return analyze_requirements(user_input)

    def run_ui_designer(self):
        return generate_ui()

    def run_codegen(self, module="example.py"):
        return generate_code(module)

    def run_fix(self, filepath):
        return self.error_ai.analyze_and_fix(filepath)

    def run_profile(self, func):
        return self.optimizer.profile_code(func)
