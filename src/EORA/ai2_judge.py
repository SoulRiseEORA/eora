
from ai_model_selector import do_task

class AI2Judge:
    def judge(self, thought: str) -> bool:
        result = do_task(
            prompt=f"다음 문장은 프롬프트로 저장할 가치가 있습니까? 답변은 '저장해' 또는 '무시해'로:\n{thought}",
            system_message="너는 AI2이며, 이오라의 내면 독백을 판단하는 역할이다. 중요하면 '저장해'라고만 대답해.",
            model="gpt-4o"
        )
        return "저장해" in result
