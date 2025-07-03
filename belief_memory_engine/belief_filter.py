
import json
from pathlib import Path

BELIEF_CONFIG_PATH = Path(__file__).parent.parent / "config" / "aura_config.json"

def load_belief_config():
    try:
        with open(BELIEF_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "forbidden_tags": ["분노", "실패", "무력감"],
            "preferred_goals": ["이해", "공감", "성장"]
        }

def is_forbidden(memory):
    config = load_belief_config()
    forbidden_tags = set(config.get("forbidden_tags", []))
    return bool(forbidden_tags & set(memory.get("tags", [])))

def is_preferred(memory):
    config = load_belief_config()
    goals = set(config.get("preferred_goals", []))
    return any(goal in memory.get("summary_prompt", "") for goal in goals)
