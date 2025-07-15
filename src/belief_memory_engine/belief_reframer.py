def suggest_reframe(belief):
    reframe_map = {
        "나는 못한다": "나는 아직 배우는 중이다",
        "나는 실패자다": "나는 다시 일어설 수 있는 사람이다",
        "사람들은 날 존중하지 않는다": "서로 존중받을 수 있는 관계를 만들 수 있다"
    }
    return reframe_map.get(belief, "새로운 관점으로 다시 생각해보는 건 어떨까요?")
