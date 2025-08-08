import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from ai_chat import EORAAI
from redis_memory import cache_to_redis
from resonance_engine import is_resonant

gpt = EORAAI()

def handle_input(user_id, input_text):
    if not is_resonant():
        return "🔇 공명이 약해 응답을 생략합니다."

    response = gpt.ask(input_text)
    cache_to_redis(user_id, response)
    return response