class TruthSense:
    def detect(self, memories):
        if not memories:
            return "아직 중심 진리가 명확히 드러나지 않았습니다."
        # 가장 많이 등장한 belief_tag를 중심 진리로
        tags = [tag for m in memories for tag in m["belief_tags"]]
        if tags:
            return f"당신의 중심 신념은 '{max(set(tags), key=tags.count)}'입니다."
        return "아직 중심 진리가 명확히 드러나지 않았습니다." 