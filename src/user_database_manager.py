#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자별 개별 데이터베이스 관리 시스템
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserDatabaseManager:
    """사용자별 개별 데이터베이스 관리자"""
    
    def __init__(self):
        """사용자 데이터베이스 관리자 초기화"""
        load_dotenv()
        
        # MongoDB 연결 설정
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = None
        self.connected = False
        
        # 사용자 데이터베이스 매핑 저장소
        self.user_db_mapping_file = "user_database_mapping.json"
        self.user_db_mapping = self._load_user_db_mapping()
        
        # 메인 데이터베이스 (사용자 관리용)
        self.main_db_name = "eora_ai_main"
        
        # 연결 시도
        self._connect_mongodb()
        
        logger.info("✅ 사용자 데이터베이스 관리자 초기화 완료")
    
    def _connect_mongodb(self):
        """MongoDB 연결"""
        try:
            self.client = MongoClient(self.mongo_uri)
            # 연결 테스트
            self.client.admin.command('ping')
            self.connected = True
            logger.info("✅ MongoDB 연결 성공")
        except Exception as e:
            logger.error(f"❌ MongoDB 연결 실패: {e}")
            self.connected = False
    
    def _load_user_db_mapping(self) -> Dict[str, str]:
        """사용자 데이터베이스 매핑 로드"""
        try:
            if os.path.exists(self.user_db_mapping_file):
                with open(self.user_db_mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"❌ 사용자 DB 매핑 로드 실패: {e}")
            return {}
    
    def _save_user_db_mapping(self):
        """사용자 데이터베이스 매핑 저장"""
        try:
            with open(self.user_db_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_db_mapping, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 사용자 DB 매핑 저장 실패: {e}")
    
    def _generate_user_db_name(self, user_id: str) -> str:
        """사용자별 고유 데이터베이스 이름 생성"""
        try:
            # 사용자 ID를 해시하여 안전한 DB 이름 생성
            hash_object = hashlib.md5(user_id.encode())
            hash_hex = hash_object.hexdigest()[:8]
            return f"eora_user_{hash_hex}"
        except Exception as e:
            logger.error(f"❌ 사용자 DB 이름 생성 실패: {e}")
            return f"eora_user_{user_id[:8]}"
    
    def create_user_database(self, user_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """새 사용자의 개별 데이터베이스 생성"""
        try:
            if not self.connected:
                raise Exception("MongoDB 연결이 되어 있지 않습니다.")
            
            # 사용자별 데이터베이스 이름 생성
            user_db_name = self._generate_user_db_name(user_id)
            
            # 이미 존재하는지 확인
            if user_id in self.user_db_mapping:
                logger.info(f"⚠️ 사용자 DB가 이미 존재합니다: {user_id}")
                return {
                    'success': True,
                    'user_db_name': self.user_db_mapping[user_id],
                    'message': '사용자 데이터베이스가 이미 존재합니다.'
                }
            
            # 사용자 데이터베이스 생성
            user_db = self.client[user_db_name]
            
            # 기본 컬렉션 생성
            collections = [
                'sessions',      # 채팅 세션
                'messages',      # 채팅 메시지
                'memories',      # 메모리
                'points',        # 포인트 정보
                'chat_logs',     # 채팅 로그
                'user_settings', # 사용자 설정
                'aura_memories', # 아우라 메모리
                'system_logs'    # 시스템 로그
            ]
            
            for collection_name in collections:
                collection = user_db[collection_name]
                # 인덱스 생성
                if collection_name == 'sessions':
                    collection.create_index([("session_id", 1)], unique=True)
                    collection.create_index([("user_id", 1)])
                    collection.create_index([("created_at", -1)])
                elif collection_name == 'messages':
                    collection.create_index([("session_id", 1)])
                    collection.create_index([("user_id", 1)])
                    collection.create_index([("timestamp", -1)])
                elif collection_name == 'points':
                    collection.create_index([("user_id", 1)], unique=True)
                elif collection_name == 'memories':
                    collection.create_index([("user_id", 1)])
                    collection.create_index([("timestamp", -1)])
                    collection.create_index([("memory_type", 1)])
            
            # 사용자 정보 저장
            user_info_collection = user_db['user_info']
            user_info['created_at'] = datetime.now().isoformat()
            user_info['database_name'] = user_db_name
            user_info_collection.insert_one(user_info)
            
            # 초기 포인트 설정 (10만 포인트)
            points_collection = user_db['points']
            initial_points = {
                'user_id': user_id,
                'current_points': 100000,  # 10만 포인트
                'total_earned': 100000,
                'total_spent': 0,
                'last_updated': datetime.now().isoformat(),
                'history': [{
                    'type': 'signup_bonus',
                    'amount': 100000,
                    'description': '신규 회원가입 보너스 (10만 포인트)',
                    'timestamp': datetime.now().isoformat()
                }]
            }
            points_collection.insert_one(initial_points)
            
            # 매핑 저장
            self.user_db_mapping[user_id] = user_db_name
            self._save_user_db_mapping()
            
            logger.info(f"✅ 사용자 데이터베이스 생성 완료: {user_id} -> {user_db_name}")
            
            return {
                'success': True,
                'user_db_name': user_db_name,
                'message': '사용자 데이터베이스가 성공적으로 생성되었습니다.',
                'initial_points': 100000
            }
            
        except Exception as e:
            logger.error(f"❌ 사용자 데이터베이스 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '사용자 데이터베이스 생성 중 오류가 발생했습니다.'
            }
    
    def get_user_database(self, user_id: str) -> Optional[pymongo.database.Database]:
        """사용자별 데이터베이스 반환"""
        try:
            if not self.connected:
                logger.error("MongoDB 연결이 되어 있지 않습니다.")
                return None
            
            if user_id not in self.user_db_mapping:
                logger.warning(f"사용자 DB 매핑이 없습니다: {user_id}")
                return None
            
            db_name = self.user_db_mapping[user_id]
            return self.client[db_name]
            
        except Exception as e:
            logger.error(f"❌ 사용자 데이터베이스 조회 실패: {e}")
            return None
    
    def get_user_collection(self, user_id: str, collection_name: str) -> Optional[pymongo.collection.Collection]:
        """사용자별 특정 컬렉션 반환"""
        try:
            user_db = self.get_user_database(user_id)
            if user_db:
                return user_db[collection_name]
            return None
        except Exception as e:
            logger.error(f"❌ 사용자 컬렉션 조회 실패: {e}")
            return None
    
    def delete_user_database(self, user_id: str) -> Dict[str, Any]:
        """사용자 데이터베이스 삭제"""
        try:
            if not self.connected:
                raise Exception("MongoDB 연결이 되어 있지 않습니다.")
            
            if user_id not in self.user_db_mapping:
                return {
                    'success': False,
                    'message': '사용자 데이터베이스가 존재하지 않습니다.'
                }
            
            db_name = self.user_db_mapping[user_id]
            
            # 데이터베이스 삭제
            self.client.drop_database(db_name)
            
            # 매핑에서 제거
            del self.user_db_mapping[user_id]
            self._save_user_db_mapping()
            
            logger.info(f"✅ 사용자 데이터베이스 삭제 완료: {user_id} -> {db_name}")
            
            return {
                'success': True,
                'message': '사용자 데이터베이스가 성공적으로 삭제되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"❌ 사용자 데이터베이스 삭제 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '사용자 데이터베이스 삭제 중 오류가 발생했습니다.'
            }
    
    def get_user_database_info(self, user_id: str) -> Dict[str, Any]:
        """사용자 데이터베이스 정보 조회"""
        try:
            if user_id not in self.user_db_mapping:
                return {
                    'exists': False,
                    'message': '사용자 데이터베이스가 존재하지 않습니다.'
                }
            
            db_name = self.user_db_mapping[user_id]
            user_db = self.client[db_name]
            
            # 컬렉션 정보 수집
            collections_info = {}
            for collection_name in user_db.list_collection_names():
                collection = user_db[collection_name]
                count = collection.count_documents({})
                collections_info[collection_name] = {
                    'document_count': count,
                    'indexes': list(collection.list_indexes())
                }
            
            return {
                'exists': True,
                'database_name': db_name,
                'collections': collections_info,
                'total_collections': len(collections_info)
            }
            
        except Exception as e:
            logger.error(f"❌ 사용자 데이터베이스 정보 조회 실패: {e}")
            return {
                'exists': False,
                'error': str(e)
            }
    
    def list_all_user_databases(self) -> List[Dict[str, Any]]:
        """모든 사용자 데이터베이스 목록 조회"""
        try:
            user_databases = []
            
            for user_id, db_name in self.user_db_mapping.items():
                db_info = self.get_user_database_info(user_id)
                db_info['user_id'] = user_id
                user_databases.append(db_info)
            
            return user_databases
            
        except Exception as e:
            logger.error(f"❌ 사용자 데이터베이스 목록 조회 실패: {e}")
            return []
    
    def backup_user_database(self, user_id: str, backup_path: str = None) -> Dict[str, Any]:
        """사용자 데이터베이스 백업"""
        try:
            if user_id not in self.user_db_mapping:
                return {
                    'success': False,
                    'message': '사용자 데이터베이스가 존재하지 않습니다.'
                }
            
            db_name = self.user_db_mapping[user_id]
            user_db = self.client[db_name]
            
            # 백업 경로 설정
            if not backup_path:
                backup_dir = Path("backups/user_databases")
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 모든 컬렉션 데이터 수집
            backup_data = {
                'user_id': user_id,
                'database_name': db_name,
                'backup_time': datetime.now().isoformat(),
                'collections': {}
            }
            
            for collection_name in user_db.list_collection_names():
                collection = user_db[collection_name]
                documents = list(collection.find({}))
                backup_data['collections'][collection_name] = documents
            
            # 백업 파일 저장
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"✅ 사용자 데이터베이스 백업 완료: {user_id} -> {backup_path}")
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'message': '사용자 데이터베이스 백업이 완료되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"❌ 사용자 데이터베이스 백업 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '사용자 데이터베이스 백업 중 오류가 발생했습니다.'
            }

# 전역 인스턴스
user_db_manager = UserDatabaseManager()

def get_user_database_manager() -> UserDatabaseManager:
    """사용자 데이터베이스 관리자 인스턴스 반환"""
    return user_db_manager 