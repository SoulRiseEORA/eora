
# ai_architect.py

import logging
from ai_context_loader import load_context_for_role
from ai_memory_writer import write_ai_memory

class AIArchitect:
    def __init__(self, ai_chat):
        self.ai_chat = ai_chat
        self.role = "AI_Architect"

    def plan_project(self, requirements: str) -> dict:
        logging.info("[AI_Architect] 프로젝트 기획 시작")
        context = load_context_for_role(self.role, base_path="ai_brain")
        prompt = context + "\n요구사항:\n" + requirements

        # Demo logic
        plan = {
            "modules": ["ui_main.py", "ai_code_generator.py", "ai_error_analyzer.py"],
            "features": ["UI/UX Tab", "Code Gen", "Error Analysis"]
        }
        result = f"기획 결과: {plan}"
        write_ai_memory(self.role, result)
        self.ai_chat.add_message("AI_Architect", result)
        return plan
