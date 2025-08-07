import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
"""aura_system/memory_pyramid.py
- Stub pyramid for hierarchical recall
"""
class MemoryPyramid:
    def __init__(self, atoms, embeddings, max_levels=4):
        self.atoms=atoms
    def find_small_pyramid(self, query_emb, top_k=1):
        return [self.atoms[:top_k]]
    def traverse_top_down(self, query_emb):
        return [self.atoms]