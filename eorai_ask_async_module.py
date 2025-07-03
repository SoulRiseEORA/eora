# eorai_ask_async_module.py
import asyncio
import re
from ai_model_selector import do_task
from aura_system.vector_store import embed_text
from aura_system.resonance_engine import calculate_resonance
from aura_system.memory_structurer import create_memory_atom
from aura_system.recall_formatter import format_recall
from EORA_Wisdom_Framework.context_classifier import classify_context
from EORA_Wisdom_Framework.memory_strategy_manager import get_turn_limit_for_context
from EORA.eora_auto_prompt_trigger import needs_recall

async def ask_async(eora_instance, user_input: str, system_message=None, chat_history: list = None) -> str:
    try:
        eora_instance.trigger.monitor_input(user_input)
        if not eora_instance.trigger.last_triggered and needs_recall(user_input):
            eora_instance.trigger.last_triggered = "회상"

        tags = [w.strip("~!?.,[]()") for w in re.findall(r'[가-힣]{2,}', user_input)]
        context = classify_context(user_input, eora_instance.emotion_flow, tags)
        turn_limit = get_turn_limit_for_context(context)

        embedding_task = asyncio.create_task(embed_text(user_input))
        summary_task = asyncio.create_task(eora_instance.mem_mgr.recall(tags, limit=3, filter_type="summary"))
        normal_task = asyncio.create_task(eora_instance.mem_mgr.recall(tags, limit=5, filter_type="normal"))
        structured_task = asyncio.create_task(eora_instance.mem_mgr.format_structured_recall("test_user", tags=tags))

        embedding = await embedding_task
        summary_atoms = await summary_task
        normal_atoms = await normal_task
        recalled_atoms = summary_atoms + normal_atoms

        linked_ids = []
        for atom in summary_atoms:
            linked_ids.extend(atom.get("linked_ids", []))
        if linked_ids:
            chained_atoms = await eora_instance.mem_mgr.load_by_ids(linked_ids)
            recalled_atoms.extend(chained_atoms)

        recall_blocks = [format_recall(atom) for atom in recalled_atoms]
        structured_recall = await structured_task

        base_prompt = system_message or eora_instance.system_prompt
        if structured_recall:
            sys_msg = "[정리된 회상 블록]\n" + structured_recall + "\n\n[지시사항]\n정보 참고하여 정확히 응답:\n" + base_prompt
            user_input = "[회상 참고] " + user_input
        elif recall_blocks:
            sys_msg = "[회상된 메모]\n" + "\n".join(recall_blocks) + "\n\n[지시사항]\n기억 기반 응답:\n" + base_prompt
            user_input = "[회상 참고] " + user_input
        else:
            sys_msg = base_prompt

        messages = [{"role": "system", "content": sys_msg}]
        for turn in eora_instance.chat_turns[-turn_limit:]:
            messages.append({"role": "user", "content": turn.get("user", "")})
            messages.append({"role": "assistant", "content": turn.get("assistant", "")})
        if chat_history:
            for turn in chat_history[-30:]:
                messages.append({"role": "user", "content": turn.get("user", "")})
                messages.append({"role": "assistant", "content": turn.get("assistant", "")})
        messages.append({"role": "user", "content": user_input})

        response = await asyncio.to_thread(do_task, messages=messages, model="gpt-4o", max_tokens=3000)

        atom = create_memory_atom(user_input, response, origin_type="user")
        if eora_instance.state_embedding is not None:
            atom["resonance_score"] = calculate_resonance(atom.get("semantic_embedding"), eora_instance.state_embedding)
        meta_id = eora_instance.insert_atom(atom)
        eora_instance.faiss.add(atom.get("semantic_embedding"), meta_id)
        eora_instance.state_embedding = embedding
        eora_instance.chat_turns.append({"user": user_input, "assistant": response})
        if len(eora_instance.chat_turns) > 30:
            eora_instance.chat_turns.pop(0)

        await eora_instance.mem_mgr.save_memory("test_user", user_input, response)
        return response + ("\n\n[회상 기반 요약]\n" + "\n".join(recall_blocks) if recall_blocks else "")
    except Exception as e:
        import traceback
        return f"[EORAAI 오류] {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
