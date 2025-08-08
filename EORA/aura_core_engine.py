
from pymongo import MongoClient
from datetime import datetime, timedelta
from ai_model_selector import do_task

class AURAEngine:
    def __init__(self):
        self.db = MongoClient("mongodb://localhost:27017")["EORA"]
        self.memory = self.db["memory_atoms"]
        self.log = self.db["selector_logs"]

    def multi_stage_selector(self, message):
        tags = self._extract_tags(message)
        results = []

        top_resonance = list(self.memory.find({"resonance_score": {"$gte": 60}})
                             .sort("resonance_score", -1).limit(5))
        results += top_resonance

        top_tags = list(self.memory.find({"tags": {"$in": tags}})
                        .sort("importance", -1).limit(5))
        results += top_tags

        connected = []
        for r in top_tags:
            ids = r.get("connections", [])
            for cid in ids:
                found = self.memory.find_one({"_id": cid})
                if found: connected.append(found)
        results += connected

        stats = list(self.memory.find().sort([("used_count", -1), ("importance", -1)]).limit(5))
        results += stats

        final = {str(doc["_id"]): doc for doc in results}.values()
        self._log_selector(message, list(final))
        return list(final)

    def fallback_search(self, message):
        return list(self.memory.find({"content": {"$regex": message, "$options": "i"}}).limit(3))

    def _extract_tags(self, message):
        tag_string = do_task(
            prompt=f"다음 문장에서 중요한 키워드를 3~5개 추출해 리스트로 출력: {message}",
            system_message="키워드 태깅기",
            model="gpt-4o"
        )
        try:
            return eval(tag_string.strip()) if tag_string.strip().startswith("[") else [tag_string.strip()]
        except:
            return [message.split()[0]]

    def _log_selector(self, message, docs):
        self.log.insert_one({
            "time": datetime.now(),
            "input": message,
            "results": [doc.get("content", "") for doc in docs],
            "used_ids": [str(doc["_id"]) for doc in docs]
        })

    def remind_queue(self, max_age_days=30):
        cutoff = datetime.now() - timedelta(days=max_age_days)
        return list(self.memory.find({"used_count": 0, "created_at": {"$lte": cutoff}}))

    def intuitive_code(self, message):
        code = sum(ord(c) for c in message) % 100000
        return f"{code:05d}"
