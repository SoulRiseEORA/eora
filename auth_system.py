"""
사용자 인증 시스템
- 로그인/로그아웃 기능
- 사용자 세션 관리
- 권한 관리
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
from database import db_manager

logger = logging.getLogger(__name__)

# JWT 시크릿 키 (실제 운영에서는 환경변수로 관리)
JWT_SECRET = "eora_ai_secret_key_2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

class AuthSystem:
    """사용자 인증 시스템"""
    
    def __init__(self):
        self.active_sessions = {}  # 세션 ID -> 사용자 정보
        self.user_sessions = {}    # 사용자 ID -> 세션 ID 목록
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_id(self) -> str:
        """세션 ID 생성"""
        return secrets.token_urlsafe(32)
    
    def create_jwt_token(self, user_id: str, is_admin: bool = False) -> str:
        """JWT 토큰 생성"""
        payload = {
            "user_id": user_id,
            "is_admin": is_admin,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT 토큰 만료")
            return None
        except jwt.InvalidTokenError:
            logger.warning("JWT 토큰 무효")
            return None
    
    async def register_user(self, username: str, password: str, email: str = None) -> Dict:
        """사용자 등록"""
        try:
            # 기존 사용자 확인
            existing_user = await db_manager.get_user_by_username(username)
            if existing_user:
                return {"success": False, "message": "이미 존재하는 사용자명입니다."}
            
            # 비밀번호 해시화
            hashed_password = self.hash_password(password)
            
            # 사용자 정보 생성
            user_data = {
                "username": username,
                "password_hash": hashed_password,
                "email": email,
                "is_admin": False,
                "created_at": datetime.now(),
                "last_login": None,
                "session_count": 0,
                "total_interactions": 0
            }
            
            # 데이터베이스에 저장
            user_id = await db_manager.create_user(user_data)
            
            logger.info(f"새 사용자 등록: {username}")
            return {
                "success": True, 
                "message": "사용자 등록이 완료되었습니다.",
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"사용자 등록 오류: {str(e)}")
            return {"success": False, "message": "사용자 등록 중 오류가 발생했습니다."}
    
    async def login_user(self, username: str, password: str) -> Dict:
        """사용자 로그인"""
        try:
            # 사용자 정보 조회
            user = await db_manager.get_user_by_username(username)
            if not user:
                return {"success": False, "message": "사용자명 또는 비밀번호가 잘못되었습니다."}
            
            # 비밀번호 검증
            hashed_password = self.hash_password(password)
            if user["password_hash"] != hashed_password:
                return {"success": False, "message": "사용자명 또는 비밀번호가 잘못되었습니다."}
            
            # 세션 ID 생성
            session_id = self.generate_session_id()
            
            # JWT 토큰 생성
            token = self.create_jwt_token(user["_id"], user.get("is_admin", False))
            
            # 세션 정보 저장
            session_data = {
                "user_id": user["_id"],
                "session_id": session_id,
                "token": token,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "ip_address": None,  # 실제 구현에서는 IP 주소 추가
                "user_agent": None   # 실제 구현에서는 User-Agent 추가
            }
            
            await db_manager.create_session(session_data)
            
            # 활성 세션에 추가
            self.active_sessions[session_id] = {
                "user_id": user["_id"],
                "username": user["username"],
                "is_admin": user.get("is_admin", False),
                "created_at": datetime.now()
            }
            
            # 사용자별 세션 목록에 추가
            if user["_id"] not in self.user_sessions:
                self.user_sessions[user["_id"]] = []
            self.user_sessions[user["_id"]].append(session_id)
            
            # 마지막 로그인 시간 업데이트
            await db_manager.update_user_last_login(user["_id"])
            
            logger.info(f"사용자 로그인: {username}")
            return {
                "success": True,
                "message": "로그인이 완료되었습니다.",
                "session_id": session_id,
                "token": token,
                "user": {
                    "user_id": user["_id"],
                    "username": user["username"],
                    "is_admin": user.get("is_admin", False),
                    "email": user.get("email")
                }
            }
            
        except Exception as e:
            logger.error(f"로그인 오류: {str(e)}")
            return {"success": False, "message": "로그인 중 오류가 발생했습니다."}
    
    async def logout_user(self, session_id: str) -> Dict:
        """사용자 로그아웃"""
        try:
            if session_id in self.active_sessions:
                user_id = self.active_sessions[session_id]["user_id"]
                
                # 활성 세션에서 제거
                del self.active_sessions[session_id]
                
                # 사용자별 세션 목록에서 제거
                if user_id in self.user_sessions:
                    if session_id in self.user_sessions[user_id]:
                        self.user_sessions[user_id].remove(session_id)
                
                # 데이터베이스에서 세션 제거
                await db_manager.remove_session(session_id)
                
                logger.info(f"사용자 로그아웃: {user_id}")
                return {"success": True, "message": "로그아웃이 완료되었습니다."}
            else:
                return {"success": False, "message": "유효하지 않은 세션입니다."}
                
        except Exception as e:
            logger.error(f"로그아웃 오류: {str(e)}")
            return {"success": False, "message": "로그아웃 중 오류가 발생했습니다."}
    
    def get_session_user(self, session_id: str) -> Optional[Dict]:
        """세션 ID로 사용자 정보 조회"""
        return self.active_sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """사용자의 활성 세션 목록 조회"""
        return self.user_sessions.get(user_id, [])
    
    async def validate_session(self, session_id: str) -> bool:
        """세션 유효성 검증"""
        if session_id not in self.active_sessions:
            return False
        
        # 세션 만료 시간 확인 (24시간)
        session_data = self.active_sessions[session_id]
        if datetime.now() - session_data["created_at"] > timedelta(hours=24):
            await self.logout_user(session_id)
            return False
        
        return True
    
    async def get_all_users(self) -> List[Dict]:
        """모든 사용자 목록 조회 (관리자용)"""
        try:
            users = await db_manager.get_all_users()
            return users
        except Exception as e:
            logger.error(f"사용자 목록 조회 오류: {str(e)}")
            return []
    
    async def get_user_stats(self, user_id: str) -> Dict:
        """사용자 통계 조회"""
        try:
            stats = await db_manager.get_user_statistics(user_id)
            return stats
        except Exception as e:
            logger.error(f"사용자 통계 조회 오류: {str(e)}")
            return {}
    
    async def delete_user(self, user_id: str) -> Dict:
        """사용자 삭제 (관리자용)"""
        try:
            # 사용자의 모든 세션 종료
            if user_id in self.user_sessions:
                for session_id in self.user_sessions[user_id]:
                    if session_id in self.active_sessions:
                        del self.active_sessions[session_id]
                del self.user_sessions[user_id]
            
            # 데이터베이스에서 사용자 삭제
            await db_manager.delete_user(user_id)
            
            logger.info(f"사용자 삭제: {user_id}")
            return {"success": True, "message": "사용자가 삭제되었습니다."}
            
        except Exception as e:
            logger.error(f"사용자 삭제 오류: {str(e)}")
            return {"success": False, "message": "사용자 삭제 중 오류가 발생했습니다."}

# 전역 인스턴스
auth_system = AuthSystem() 