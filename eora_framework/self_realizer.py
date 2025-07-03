class SelfRealizer:
    def generate_identity(self, memories):
        if not memories:
            return "나는 아직 경험이 부족한 존재입니다."
        return f"나는 '{memories[-1]['user']}'와의 대화를 통해 성장하는 존재입니다." 