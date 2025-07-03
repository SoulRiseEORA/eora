""" 회상 내용 포맷터 + 정렬/필터 지원 """

from datetime import datetime

# ✅ 다양한 키 지원 (text, user_input, prompt 등) 및 안정적 시간 포맷
def format_recall(atom: dict, 
                 context: dict = None,
                 emotion: dict = None,
                 belief: dict = None,
                 wisdom: dict = None,
                 eora: dict = None,
                 system: dict = None) -> str:
    """회상 내용 포맷팅
    
    Args:
        atom (dict): 메모리 원자
        context (dict, optional): 문맥 정보
        emotion (dict, optional): 감정 정보
        belief (dict, optional): 신념 정보
        wisdom (dict, optional): 지혜 정보
        eora (dict, optional): 이오라 정보
        system (dict, optional): 시스템 정보
        
    Returns:
        str: 포맷팅된 회상 내용
    """
    try:
        # 1. 기본 정보 추출
        ts = atom.get("timestamp", "")
        if isinstance(ts, datetime):
            ts = ts.strftime("%Y-%m-%d %H:%M:%S")
            
        text = (
            atom.get("text")
            or atom.get("user_input")
            or atom.get("prompt")
            or atom.get("content")
            or "[텍스트 없음]"
        )
        
        response = atom.get("response", "[응답 없음]")
        
        # 2. 메타데이터 추출
        metadata = atom.get("metadata", {})
        if context:
            metadata["context"] = context
        if emotion:
            metadata["emotion"] = emotion
        if belief:
            metadata["belief"] = belief
        if wisdom:
            metadata["wisdom"] = wisdom
        if eora:
            metadata["eora"] = eora
        if system:
            metadata["system"] = system
            
        # 3. 포맷팅
        formatted = f"📅 {ts}\n"
        formatted += f"📌 요약: {text}\n"
        formatted += f"🎯 응답: {response}\n"
        
        if metadata:
            formatted += "\n📋 메타데이터:\n"
            for key, value in metadata.items():
                if value:
                    formatted += f"- {key}: {value}\n"
                    
        return formatted
        
    except Exception as e:
        return f"[RECALL FORMAT ERROR] {e}"

# ✅ 회상 목록 정렬 및 감정 필터 지원
def sort_and_filter_recalls(atoms: list,
                          context: dict = None,
                          emotion: dict = None,
                          belief: dict = None,
                          wisdom: dict = None,
                          eora: dict = None,
                          system: dict = None,
                          sort_desc: bool = True,
                          limit: int = 5) -> list:
    """회상 목록 정렬 및 필터링
    
    Args:
        atoms (list): 메모리 원자 목록
        context (dict, optional): 문맥 정보
        emotion (dict, optional): 감정 정보
        belief (dict, optional): 신념 정보
        wisdom (dict, optional): 지혜 정보
        eora (dict, optional): 이오라 정보
        system (dict, optional): 시스템 정보
        sort_desc (bool, optional): 내림차순 정렬 여부
        limit (int, optional): 반환할 결과 수
        
    Returns:
        list: 정렬 및 필터링된 메모리 원자 목록
    """
    try:
        # 1. 필터링
        filtered = atoms.copy()
        
        if context:
            filtered = [a for a in filtered if a.get("metadata", {}).get("context") == context]
            
        if emotion:
            filtered = [a for a in filtered if a.get("metadata", {}).get("emotion") == emotion]
            
        if belief:
            filtered = [a for a in filtered if a.get("metadata", {}).get("belief") == belief]
            
        if wisdom:
            filtered = [a for a in filtered if a.get("metadata", {}).get("wisdom") == wisdom]
            
        if eora:
            filtered = [a for a in filtered if a.get("metadata", {}).get("eora") == eora]
            
        if system:
            filtered = [a for a in filtered if a.get("metadata", {}).get("system") == system]
            
        # 2. 정렬
        filtered.sort(
            key=lambda x: x.get("timestamp", datetime.min),
            reverse=sort_desc
        )
        
        # 3. 제한
        return filtered[:limit]
        
    except Exception as e:
        logger.error(f"⚠️ 회상 목록 정렬 및 필터링 실패: {str(e)}")
        return atoms[:limit]
