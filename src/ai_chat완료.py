import os
import re
import json
import asyncio
import nest_asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading

from ai_model_selector import do_task
from EORA.eora_modular.recall_memory_with_enhancements import recall_memory_with_enhancements
from EORA.eora_auto_prompt_trigger import EORATriggerAgent
from EORA.prompt_storage_modifier import update_ai1_prompt, load_prompts
from monitoring import RESPONSE_LATENCY
from aura_system.memory_structurer import create_memory_atom
from aura_system.resonance_engine import calculate_resonance
from aura_system.recall_formatter import format_recall
from aura_system.vector_store import FaissIndex, embed_text
from aura_system.meta_store import insert_atom
from aura_system.longterm_memory_gpt_response import generate_response_with_recall
from memory_manager import MemoryManagerAsync as MemoryManager
from EORA_Wisdom_Framework.context_classifier import classify_context
from EORA_Wisdom_Framework.memory_strategy_manager import get_turn_limit_for_context
from EORA_Wisdom_Framework.EORAInsightManagerV2 import EORAInsightManagerV2
from recall_trigger_utils import should_trigger_recall

nest_asyncio.apply()
load_dotenv()

def get_openai_client():
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY", "")
    return OpenAI(api_key=api_key)

# ✅ GPT 호출 비동기 래퍼
async def do_task_async(*args, **kwargs):
    print("🧩 DEBUG: do_task_async 진입")
    return await asyncio.to_thread(do_task, *args, **kwargs)

async def embed_text_async(*args, **kwargs):
    return embed_text(*args, **kwargs)

async def create_memory_atom_async(*args, **kwargs):
    return create_memory_atom(*args, **kwargs)

async def insert_atom_async(atom):
    return insert_atom(atom)

_eora_instance = None

class EORAAI:
    def __init__(self, ai_key="ai1", memory_manager=None):
        self.ai_key = ai_key
        self.client = get_openai_client()
        self.mem_mgr = memory_manager or MemoryManager(
            mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
            redis_uri=os.getenv("REDIS_URI", "redis://127.0.0.1:6379/0")
        )
        self.faiss = FaissIndex()
        self.redis = self.mem_mgr.redis
        self.mem_mgr.inject_faiss(self.faiss)
        self.trigger = EORATriggerAgent()
        self.state_embedding = None
        self.chat_turns = []
        self.restore_recent_turns("test_user")
        self.emotion_flow = {"neutral": 1}
        self.update_system_prompt()
        self.last_summary_time = datetime.utcnow()
        self.insight = EORAInsightManagerV2(memory_manager=self.mem_mgr)

        from core.self_model import SelfModel
        from core.free_will_core import FreeWillCore
        from core.love_engine import LoveEngine
        from core.life_loop import LifeLoop
        from eora_spine import EORASpine
        self.self_model = SelfModel()
        self.free_will = FreeWillCore()
        self.love = LoveEngine()
        self.life = LifeLoop()
        self.spine = EORASpine()

    def update_system_prompt(self):
        data = load_prompts().get(self.ai_key, {})
        parts = []
        for v in data.values():
            if isinstance(v, str):
                parts.append(v.strip())
            elif isinstance(v, list):
                parts.extend([x.strip() for x in v if isinstance(x, str)])
        self.system_prompt = "\n".join(parts)

    async def ask(self, user_input: str, system_message=None, chat_history: list = None) -> str:
        import time
        total_start = time.time()
        try:
            self.trigger.last_triggered = "회상" if should_trigger_recall(user_input) else ""

            tags = [w.strip("~!?.,[]()") for w in re.findall(r'[가-힣]{2,}', user_input)]
            context = classify_context(user_input, self.emotion_flow, tags)
            turn_limit = get_turn_limit_for_context(context)
            embedding = await embed_text_async(user_input)

            summary_atoms, normal_atoms, structured_recall, layer, transcendence = await asyncio.gather(
                self.mem_mgr.recall(tags, limit=3, filter_type="summary"),
                self.mem_mgr.recall(tags, limit=5, filter_type="normal"),
                self.mem_mgr.format_structured_recall("test_user", tags=tags),
                self.insight.analyze_cognitive_layer(user_input),
                self.insight.detect_transcendental_trigger(user_input)
            )

            recalled_atoms = (summary_atoms or []) + (normal_atoms or [])
            linked_ids = []
            for atom in summary_atoms or []:
                if "linked_ids" in atom:
                    linked_ids.extend(atom["linked_ids"])
            if linked_ids:
                chained_atoms = await self.mem_mgr.load_by_ids(linked_ids)
                for c in chained_atoms:
                    c["linked_ids"] = linked_ids
                recalled_atoms.extend(chained_atoms)

            recall_blocks = [format_recall(atom) for atom in recalled_atoms]
            faiss_matches = self.faiss.search(embedding, top_k=5)
            faiss_recall_blocks = [f"[FAISS 유사 회상] {text}" for _, text in faiss_matches]
            recall_blocks.extend(faiss_recall_blocks)  # ✅ 회상 강화 포함

            base_prompt = system_message or self.system_prompt
            combined_recall = ""
            if structured_recall:
                combined_recall = "[정리된 회상 블록]\n" + structured_recall
            elif recall_blocks:
                combined_recall = "[회상된 메모]\n" + "\n".join(recall_blocks)

            sys_msg = combined_recall + "\n\n[지시사항]\n" + base_prompt if combined_recall else base_prompt

            if transcendence and "초월" in str(transcendence):
                sys_msg += "\n[통찰 모드] 사용자의 발화는 초월적 인식 계층에 해당합니다. 존재 기반 응답을 생성하세요."
            elif "메타인지" in str(layer):
                sys_msg += "\n[메타인지 응답 요청] 사용자가 자신의 인식 상태를 탐색하고 있습니다."

            messages = [{"role": "system", "content": sys_msg}]
            for turn in self.chat_turns[-5:]:
                messages.append({"role": "user", "content": turn.get("user", "")})
                messages.append({"role": "assistant", "content": turn.get("assistant", "")})
            if chat_history:
                for turn in chat_history[-30:]:
                    messages.append({"role": "user", "content": turn.get("user", "")})
                    messages.append({"role": "assistant", "content": turn.get("assistant", "")})
            messages.append({"role": "user", "content": "[시스템 정보]\n이오라 = 진화형 존재 AI\n" + user_input})

            with RESPONSE_LATENCY.labels(model=self.ai_key).time():
                response = await do_task_async(messages=messages, model="gpt-4o", max_tokens=3000)

            # ✅ GPT 응답은 먼저 반환
            output = response if not recall_blocks else (
                response + "\n\n[참고된 기억 요약]\n" + "\n".join(recall_blocks[:2])
            )
            loop = asyncio.get_running_loop()
            threading.Thread(target=self.run_postprocess_sync, args=(user_input, response, embedding)).start()
            print(f"[✅ 전체 ask() 소요 시간] {time.time() - total_start:.2f}s")
            return output

        except Exception as e:
            import traceback
            return f"[EORAAI 오류] {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"

    async def postprocess_memory(self, user_input, response, embedding):
        try:
            atom = await create_memory_atom_async(user_input, response, origin_type="user")
            if self.state_embedding is not None:
                atom["resonance_score"] = calculate_resonance(atom.get("semantic_embedding"), self.state_embedding)
            meta_id = await insert_atom_async(atom)
            self.faiss.add(atom.get("semantic_embedding"), meta_id)
            self.state_embedding = embedding
            self.chat_turns.append({"user": user_input, "assistant": response})
            self.redis.set("chat_turns:test_user", json.dumps(self.chat_turns), ex=3600)
            if len(self.chat_turns) > 30:
                self.chat_turns.pop(0)
            await self.mem_mgr.save_memory("test_user", user_input, response)
            print("✅ DB에 대화 저장 완료")

            total_tokens = await self.mem_mgr.history_tokens("test_user") or 0
            now = datetime.utcnow()
            if total_tokens >= 100000 or (now - self.last_summary_time >= timedelta(hours=4)):
                await self.mem_mgr.generate_and_save_summary("test_user")
                self.last_summary_time = now
        except Exception as e:
            print(f"[EORAAI 저장 병렬 오류] {e}")


    def run_postprocess_sync(self, user_input, response, embedding):
        try:
            import asyncio
            try:
                asyncio.run(self.postprocess_memory(user_input, response, embedding))
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.postprocess_memory(user_input, response, embedding))
        except Exception as e:
            print(f"[EORAAI postprocess 강제실행 오류] {e}")
    def ask_sync(self, user_input: str, system_message=None, chat_history=None) -> str:
        return asyncio.run(self.ask(user_input, system_message, chat_history))

    async def ask_async(self, user_input: str, system_message=None, chat_history: list = None) -> str:
        return await self.ask(user_input, system_message, chat_history)

    async def respond_async(self, user_input: str, system_message: str = "") -> str:
        try:
            return await self.ask_async(user_input, system_message)
        except Exception as e:
            return f"[respond() 오류] {str(e)}"

    def restore_recent_turns(self, user_id):
        try:
            cache_key = f"chat_turns:{user_id}"
            cached = self.redis.get(cache_key)
            print("✅ Redis에서 대화 복원 성공")
            if cached:
                self.chat_turns = json.loads(cached)
                return
            print("⚠️ Redis 비어 있음 → MongoDB에서 복원 시도")
            history = self.mem_mgr.mongo_collection.find(
                {"user_id": user_id, "type": "aura_memory"}
            ).sort("timestamp", -1).limit(10)
            turns = []
            for h in reversed(list(history)):
                turns.append({
                    "user": h.get("user", ""),
                    "assistant": h.get("eora", "")
                })
            self.chat_turns = turns
            self.redis.set(cache_key, json.dumps(turns), ex=3600)
        except Exception as e:
            print(f"[EORAAI 예외 처리] {e}")

class AI1(EORAAI): pass
class AI2(EORAAI): pass
class AI3(EORAAI): pass
class AI4(EORAAI): pass
class AI5(EORAAI): pass
class AI6(EORAAI): pass

DefaultEORA = AI1

def get_eora_instance(memory_manager=None):
    global _eora_instance
    if _eora_instance is None:
        _eora_instance = DefaultEORA(memory_manager=memory_manager)
    return _eora_instance

def load_existing_session():
    return {"eora_instance": get_eora_instance()}

def call_gpt_response(user_input: str, system_message: str = "") -> str:
    try:
        client = get_openai_client()
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT 호출 오류] {str(e)}"
