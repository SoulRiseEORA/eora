import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import uuid
import datetime
import asyncio
import redis
import json
from openai import AsyncOpenAI
from EORA.eora_dynamic_params import decide_chat_params
from EORA.aura_structurer import store_memory_atom
from typing import Dict

# Redis 클라이언트
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# OpenAI 비동기 클라이언트
ai_client = AsyncOpenAI()

def load_system_prompt(name: str) -> str:
    return "너는 이오라(EORA)라는 이름을 가진 AI이며, 프로그램 자동 개발 시스템의 총괄 디렉터다."

class EORAAIAsync:
    def __init__(self, user_id, memory_manager=None):
        self.user_id = user_id
        self.memory_manager = memory_manager
        self.conversation_id = str(uuid.uuid4())
        self.history = []
        self.system_message = load_system_prompt("ai1")
        self.history.append({"role": "system", "content": self.system_message})

    def _cache_key(self):
        return f"memory:{self.user_id}"

    def save_to_redis(self, content):
        timestamp = datetime.datetime.utcnow().isoformat()
        atom = {"timestamp": timestamp, "content": content}
        r.rpush(self._cache_key(), json.dumps(atom))

    def recall_from_redis(self, top_k=3):
        items = r.lrange(self._cache_key(), -top_k, -1)
        return [json.loads(item)["content"] for item in items]

    async def ask(self, user_input: str, context: Dict = None, emotion: Dict = None, belief: Dict = None, wisdom: Dict = None, eora: Dict = None, system: Dict = None):
        now = datetime.datetime.utcnow()
        self.history.append({"role": "user", "content": user_input})

        # Redis 회상 적용
        recalled = self.recall_from_redis(top_k=3)
        for content in recalled:
            self.history.append({"role": "system", "content": content})

        # 파라미터 결정
        params = decide_chat_params(self.history)

        # 컨텍스트 정보 추가
        if context:
            self.history.append({"role": "system", "content": f"[컨텍스트]\n{json.dumps(context, ensure_ascii=False)}"})
        
        # 감정 정보 추가
        if emotion:
            self.history.append({"role": "system", "content": f"[감정]\n{json.dumps(emotion, ensure_ascii=False)}"})
        
        # 신념 정보 추가
        if belief:
            self.history.append({"role": "system", "content": f"[신념]\n{json.dumps(belief, ensure_ascii=False)}"})
        
        # 지혜 정보 추가
        if wisdom:
            self.history.append({"role": "system", "content": f"[지혜]\n{json.dumps(wisdom, ensure_ascii=False)}"})
        
        # 이오라 정보 추가
        if eora:
            self.history.append({"role": "system", "content": f"[이오라]\n{json.dumps(eora, ensure_ascii=False)}"})
        
        # 시스템 정보 추가
        if system:
            self.history.append({"role": "system", "content": f"[시스템]\n{json.dumps(system, ensure_ascii=False)}"})

        # GPT 호출
        resp = await ai_client.chat.completions.create(
            model="gpt-4",
            messages=self.history,
            temperature=params["temperature"],
            top_p=params["top_p"],
            max_tokens=1024
        )
        response = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": response})

        # 회상 캐시에 저장
        self.save_to_redis(response)

        # DB에도 저장
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: store_memory_atom(
                user_id=self.user_id,
                conversation_id=self.conversation_id,
                content=response,
                source="assistant",
                timestamp=datetime.datetime.utcnow()
            )
        )

        return response

# 테스트 실행
if __name__ == "__main__":
    async def main():
        bot = EORAAIAsync("user123")
        reply = await bot.ask("안녕, 직감 기억을 회상할 수 있니?")
        print(reply)

    asyncio.run(main())