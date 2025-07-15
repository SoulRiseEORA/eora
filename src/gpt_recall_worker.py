from PyQt5.QtCore import QThread, pyqtSignal
import traceback
import asyncio

class GPTRecallWorker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, eora, message: str, session_id="test_user", parent=None):
        super().__init__(parent)
        self.eora = eora
        self.message = message
        self.session_id = session_id

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.handle_recall())
            self.result_ready.emit(result)
        except Exception as e:
            err = f"[GPTRecallWorker Error] {type(e).__name__}: {e}\n{traceback.format_exc()}"
            self.error_occurred.emit(err)

    async def handle_recall(self) -> str:
        try:
            self.eora.trigger.monitor_input(self.message)

            if not self.eora.trigger.last_triggered and self.eora.needs_recall(self.message):
                self.eora.trigger.last_triggered = "회상"

            tags = [w.strip("~!?.,[]()") for w in self.message.split() if len(w) >= 2]

            summary_atoms = await self.eora.mem_mgr.recall(tags, limit=3, filter_type="summary")
            normal_atoms = await self.eora.mem_mgr.recall(tags, limit=5, filter_type="normal")
            recalled_atoms = summary_atoms + normal_atoms

            linked_ids = []
            for atom in summary_atoms:
                if "linked_ids" in atom:
                    linked_ids.extend(atom["linked_ids"])
            if linked_ids:
                chained_atoms = await self.eora.mem_mgr.load_by_ids(linked_ids)
                recalled_atoms.extend(chained_atoms)

            recall_blocks = [self.eora.format_recall(atom) for atom in recalled_atoms]
            structured = await self.eora.mem_mgr.format_structured_recall(self.session_id, tags=tags)

            # GPT 호출
            user_input = "[회상 참고] " + self.message
            base_prompt = self.eora.system_prompt

            if structured:
                sys_msg = "[정리된 회상 블록]\n" + structured + "\n\n[지시사항]\n이 회상을 참고해 응답하세요.\n" + base_prompt
            elif recall_blocks:
                sys_msg = "[회상된 메모]\n" + "\n".join(recall_blocks) + "\n\n[지시사항]\n이 메모를 참고해 응답하세요.\n" + base_prompt
            else:
                sys_msg = base_prompt

            messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_input}]
            response = self.eora.do_task(messages=messages, model="gpt-4o")

            return response
        except Exception as e:
            return f"[handle_recall Exception] {e}"