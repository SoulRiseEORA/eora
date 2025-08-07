import re
from aura_system.retrieval_pipeline import retrieve
from aura_system.vector_store import embed_text

async def recall_memory(user_input: str, query_emb: list = None) -> list:
    """메모리 회상
    
    Args:
        user_input (str): 사용자 입력
        query_emb (list, optional): 쿼리 임베딩
        
    Returns:
        list: 회상된 메모리 목록
    """
    # 키워드 + 임베딩 기반 검색
    keywords = re.findall(r"[가-힣]{2,5}", user_input)
    if not keywords:
        return []

    if query_emb is None:
        query_emb = await embed_text(user_input)
    recalled_atoms = await retrieve(query_emb, keywords, top_k=3)
    return recalled_atoms
