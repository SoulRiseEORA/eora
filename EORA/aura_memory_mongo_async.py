"""
Stub for aura_memory_mongo_async to avoid blocking imports.
Redirects to MemoryManager from memory_manager.py
"""

import asyncio
import os
from memory_manager import MemoryManager

# Initialize MemoryManager later in main
mem_mgr = None

def init_memory_manager(mongo_uri, loop):
    global mem_mgr
    mem_mgr = MemoryManager(mongo_uri, loop)

async def ensure_indexes():
    # No-op or could schedule real indexes if needed
    return

def save_memory_batch(entry):
    if mem_mgr:
        # schedule async save
        asyncio.run_coroutine_threadsafe(mem_mgr.save(entry), mem_mgr.loop)
    else:
        print("⚠️ MemoryManager not initialized.")

