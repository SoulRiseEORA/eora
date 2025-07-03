from aura_system.memory_manager import MemoryManagerAsync
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mongodb():
    try:
        manager = MemoryManagerAsync.get_instance()
        await manager.initialize()
        logger.info("✅ MongoDB connection test completed")
    except Exception as e:
        logger.error(f"❌ MongoDB connection test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_mongodb()) 