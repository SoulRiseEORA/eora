from aura_system.memory_structurer import MemoryAtom
from aura_system.meta_store import get_meta_store
from aura_system.vector_store import embed_text, FaissIndex

# 🧠 메모리 삽입
async def create_memory_atom_async(content: str, metadata: dict = None, **kwargs):
    """
    MemoryAtom을 비동기적으로 생성합니다.
    kwargs로 role 등을 받아 metadata에 통합합니다.
    """
    final_metadata = metadata or {}
    if 'role' in kwargs:
        final_metadata['role'] = kwargs['role']
    
    # 다른 kwargs도 메타데이터에 추가할 수 있습니다.
    for key, value in kwargs.items():
        if key not in ['role']: # 이미 처리한 role은 제외
             final_metadata[key] = value

    return MemoryAtom(content=content, metadata=final_metadata)

_meta_store_cache = None

async def insert_atom_async(atom: MemoryAtom):
    """MemoryAtom 객체를 받아 메타데이터를 저장합니다."""
    global _meta_store_cache
    # 메타 저장소 인스턴스를 한 번만 가져와 캐시합니다.
    if _meta_store_cache is None:
        _meta_store_cache = await get_meta_store()
    
    meta_store = _meta_store_cache
    
    # atom 객체에서 memory_id와 metadata를 추출하여 저장
    # store_metadata는 비동기 함수이므로 await을 사용합니다.
    return await meta_store.store_metadata(
        memory_id=atom.memory_id,
        metadata=atom.metadata
    )

# 🔍 벡터 임베딩
async def embed_text_async(*args, **kwargs):
    return embed_text(*args, **kwargs)
