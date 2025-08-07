"""
engine_base.py
- 기본 엔진 클래스
- 모든 엔진의 기본이 되는 추상 클래스
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import numpy as np
from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pathlib import Path

# 상대 경로 임포트
from aura_system.config import get_config
from aura_system.memory_structurer import MemoryAtom
from aura_system.embeddings import get_embeddings
from aura_system.vector_store import get_vector_store
from aura_system.memory_store import get_memory_store
from aura_system.meta_store import get_meta_store
from aura_system.memory_chain import get_memory_chain
from aura_system.recall_memory_with_enhancements import get_recall_enhancer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseEngine:
    """기본 엔진 클래스"""
    
    def __init__(self):
        self.config = get_config()
        self.initialized = False
        
    async def initialize(self) -> bool:
        """엔진 초기화"""
        try:
            if self.initialized:
                return True
                
            # 컴포넌트 초기화
            self.memory_manager = await get_memory_manager()
            self.embeddings = await get_embeddings()
            self.vector_store = await get_vector_store()
            self.memory_store = await get_memory_store()
            self.meta_store = await get_meta_store()
            self.memory_chain = await get_memory_chain()
            self.recall_enhancer = await get_recall_enhancer()
            
            self.initialized = True
            logger.info(f"✅ {self.__class__.__name__} 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.__class__.__name__} 초기화 실패: {str(e)}")
            return False
            
    async def process(self, message: str) -> str:
        """메시지 처리 (하위 클래스에서 구현)"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다.")
        
    async def cleanup(self):
        """리소스 정리"""
        try:
            if hasattr(self, 'memory_manager'):
                await self.memory_manager.cleanup()
                
            logger.info(f"✅ {self.__class__.__name__} 리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ {self.__class__.__name__} 정리 중 오류 발생: {str(e)}")
            
    def __del__(self):
        """소멸자"""
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(self.cleanup())
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.cleanup())
            loop.close() 