"""aura_system/gpt_conversation_hook.py
- Corrected indentation and package imports
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from aura_system.memory_structurer import create_memory_atom
from aura_system.resonance_engine import calculate_resonance
from aura_system.aura_selector import aura_selector_hierarchical
from aura_system.recall_formatter import format_recall
from aura_system.memory_store import memory_store

class ConversationHook:
    def __init__(self):
        self.store = memory_store
        self.current_state_embedding = None

    def on_message(self, user_text: str, gpt_func) -> str:
        gpt_resp = gpt_func(user_text)
        atom = create_memory_atom(user_text, gpt_resp)
        if self.current_state_embedding is not None:
            atom['resonance_score'] = calculate_resonance(
                atom['embedding'], self.current_state_embedding
            )
        self.store.insert(atom)
        query_embedding = atom['embedding']
        selected = aura_selector_hierarchical(query_embedding, self.store.list())
        recall_text = "\n".join(format_recall(m) for m in selected)
        self.current_state_embedding = query_embedding
        return f"{gpt_resp}\n\n{recall_text}"