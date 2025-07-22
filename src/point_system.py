"""
EORA AI System - 포인트 시스템 및 결제 관리
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    CRYPTO = "crypto"

class PointPackage(BaseModel):
    id: str
    name: str
    points: int
    price: float
    currency: str = "KRW"
    description: str
    is_popular: bool = False
    discount_percent: int = 0

class PaymentTransaction(BaseModel):
    id: str
    user_id: str
    package_id: str
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    transaction_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class UserPoints(BaseModel):
    user_id: str
    current_points: int
    total_earned: int
    total_spent: int
    last_updated: datetime
    history: List[Dict[str, Any]] = []

class PointSystem:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.packages = self._initialize_packages()
        
    def _initialize_packages(self) -> List[PointPackage]:
        """기본 포인트 패키지 초기화"""
        return [
            PointPackage(
                id="starter",
                name="스타터 패키지",
                points=100,
                price=5000,
                description="처음 시작하는 분들을 위한 패키지",
                is_popular=False
            ),
            PointPackage(
                id="basic",
                name="기본 패키지",
                points=500,
                price=20000,
                description="일반적인 사용을 위한 패키지",
                is_popular=True
            ),
            PointPackage(
                id="premium",
                name="프리미엄 패키지",
                points=1500,
                price=50000,
                description="많은 대화를 원하는 분들을 위한 패키지",
                discount_percent=10
            ),
            PointPackage(
                id="unlimited",
                name="무제한 패키지",
                points=5000,
                price=150000,
                description="무제한 대화를 위한 패키지",
                discount_percent=20
            )
        ]
    
    async def get_user_points(self, user_id: str) -> Optional[UserPoints]:
        """사용자의 포인트 정보 조회"""
        try:
            collection = self.db_manager.db.user_points
            doc = await collection.find_one({"user_id": user_id})
            
            if doc:
                return UserPoints(**doc)
            else:
                # 새 사용자라면 기본 포인트 생성
                return await self.create_user_points(user_id)
        except Exception as e:
            logger.error(f"사용자 포인트 조회 오류: {str(e)}")
            return None
    
    async def create_user_points(self, user_id: str) -> UserPoints:
        """새 사용자의 포인트 계정 생성 (회원가입 시 100포인트 지급)"""
        try:
            user_points = UserPoints(
                user_id=user_id,
                current_points=100,  # 회원가입 보너스
                total_earned=100,
                total_spent=0,
                last_updated=datetime.now(),
                history=[{
                    "type": "signup_bonus",
                    "points": 100,
                    "description": "회원가입 보너스",
                    "timestamp": datetime.now()
                }]
            )
            
            collection = self.db_manager.db.user_points
            await collection.insert_one(user_points.dict())
            
            logger.info(f"새 사용자 포인트 계정 생성: {user_id}")
            return user_points
        except Exception as e:
            logger.error(f"사용자 포인트 계정 생성 오류: {str(e)}")
            return None
    
    async def add_points(self, user_id: str, points: int, reason: str, metadata: Dict[str, Any] = None) -> bool:
        """포인트 추가"""
        try:
            collection = self.db_manager.db.user_points
            now = datetime.now()
            
            # 포인트 업데이트
            result = await collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "current_points": points,
                        "total_earned": points
                    },
                    "$set": {"last_updated": now},
                    "$push": {
                        "history": {
                            "type": "earned",
                            "points": points,
                            "description": reason,
                            "timestamp": now,
                            "metadata": metadata or {}
                        }
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"포인트 추가 완료: {user_id}, {points}포인트, 사유: {reason}")
                return True
            else:
                logger.error(f"포인트 추가 실패: {user_id}")
                return False
        except Exception as e:
            logger.error(f"포인트 추가 오류: {str(e)}")
            return False
    
    async def use_points(self, user_id: str, points: int, reason: str, metadata: Dict[str, Any] = None) -> bool:
        """포인트 사용"""
        try:
            # 현재 포인트 확인
            user_points = await self.get_user_points(user_id)
            if not user_points or user_points.current_points < points:
                logger.warning(f"포인트 부족: {user_id}, 필요: {points}, 보유: {user_points.current_points if user_points else 0}")
                return False
            
            collection = self.db_manager.db.user_points
            now = datetime.now()
            
            # 포인트 차감
            result = await collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "current_points": -points,
                        "total_spent": points
                    },
                    "$set": {"last_updated": now},
                    "$push": {
                        "history": {
                            "type": "spent",
                            "points": -points,
                            "description": reason,
                            "timestamp": now,
                            "metadata": metadata or {}
                        }
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"포인트 사용 완료: {user_id}, {points}포인트, 사유: {reason}")
                return True
            else:
                logger.error(f"포인트 사용 실패: {user_id}")
                return False
        except Exception as e:
            logger.error(f"포인트 사용 오류: {str(e)}")
            return False
    
    async def get_available_packages(self) -> List[PointPackage]:
        """사용 가능한 포인트 패키지 조회"""
        return self.packages
    
    async def create_payment(self, user_id: str, package_id: str, payment_method: PaymentMethod) -> Optional[PaymentTransaction]:
        """결제 트랜잭션 생성"""
        try:
            # 패키지 정보 확인
            package = next((p for p in self.packages if p.id == package_id), None)
            if not package:
                logger.error(f"존재하지 않는 패키지: {package_id}")
                return None
            
            # 결제 트랜잭션 생성
            payment = PaymentTransaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                package_id=package_id,
                amount=package.price,
                currency=package.currency,
                payment_method=payment_method,
                status=PaymentStatus.PENDING,
                created_at=datetime.now()
            )
            
            # 데이터베이스에 저장
            collection = self.db_manager.db.payment_transactions
            await collection.insert_one(payment.dict())
            
            logger.info(f"결제 트랜잭션 생성: {payment.id}, 사용자: {user_id}, 패키지: {package_id}")
            return payment
        except Exception as e:
            logger.error(f"결제 트랜잭션 생성 오류: {str(e)}")
            return None
    
    async def complete_payment(self, payment_id: str, transaction_id: str = None) -> bool:
        """결제 완료 처리"""
        try:
            collection = self.db_manager.db.payment_transactions
            
            # 결제 정보 조회
            payment_doc = await collection.find_one({"id": payment_id})
            if not payment_doc:
                logger.error(f"존재하지 않는 결제: {payment_id}")
                return False
            
            payment = PaymentTransaction(**payment_doc)
            
            # 결제 상태 업데이트
            await collection.update_one(
                {"id": payment_id},
                {
                    "$set": {
                        "status": PaymentStatus.COMPLETED,
                        "completed_at": datetime.now(),
                        "transaction_id": transaction_id
                    }
                }
            )
            
            # 포인트 지급
            package = next((p for p in self.packages if p.id == payment.package_id), None)
            if package:
                success = await self.add_points(
                    payment.user_id,
                    package.points,
                    f"포인트 패키지 구매: {package.name}",
                    {"payment_id": payment_id, "package_id": package.id}
                )
                
                if success:
                    logger.info(f"결제 완료 및 포인트 지급: {payment_id}, 사용자: {payment.user_id}")
                    return True
                else:
                    logger.error(f"포인트 지급 실패: {payment_id}")
                    return False
            else:
                logger.error(f"패키지 정보 없음: {payment.package_id}")
                return False
        except Exception as e:
            logger.error(f"결제 완료 처리 오류: {str(e)}")
            return False
    
    async def get_payment_history(self, user_id: str, limit: int = 50) -> List[PaymentTransaction]:
        """사용자의 결제 내역 조회"""
        try:
            collection = self.db_manager.db.payment_transactions
            cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
            
            payments = []
            async for doc in cursor:
                payments.append(PaymentTransaction(**doc))
            
            return payments
        except Exception as e:
            logger.error(f"결제 내역 조회 오류: {str(e)}")
            return []
    
    async def get_point_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """사용자의 포인트 사용 내역 조회"""
        try:
            user_points = await self.get_user_points(user_id)
            if not user_points:
                return []
            
            # 최근 내역만 반환
            return user_points.history[-limit:] if len(user_points.history) > limit else user_points.history
        except Exception as e:
            logger.error(f"포인트 내역 조회 오류: {str(e)}")
            return []
    
    async def check_chat_cost(self, user_id: str, message_length: int = 0) -> Dict[str, Any]:
        """채팅 비용 계산 및 포인트 확인"""
        # 간단한 비용 계산 (메시지 길이에 따라)
        base_cost = 1  # 기본 1포인트
        length_cost = max(0, (message_length - 100) // 50)  # 100자 초과시 50자당 1포인트 추가
        total_cost = base_cost + length_cost
        
        user_points = await self.get_user_points(user_id)
        can_chat = user_points and user_points.current_points >= total_cost
        
        return {
            "can_chat": can_chat,
            "cost": total_cost,
            "current_points": user_points.current_points if user_points else 0,
            "remaining_points": (user_points.current_points - total_cost) if user_points and can_chat else 0
        }
    
    async def charge_chat_cost(self, user_id: str, message_length: int = 0, chat_id: str = None) -> bool:
        """채팅 비용 차감"""
        cost_info = await self.check_chat_cost(user_id, message_length)
        
        if not cost_info["can_chat"]:
            return False
        
        return await self.use_points(
            user_id,
            cost_info["cost"],
            "GPT 채팅 비용",
            {"chat_id": chat_id, "message_length": message_length}
        )

class AdminPointManager:
    """관리자용 포인트 관리 시스템"""
    
    def __init__(self, point_system: PointSystem):
        self.point_system = point_system
    
    async def get_all_users_points(self) -> List[UserPoints]:
        """모든 사용자의 포인트 정보 조회"""
        try:
            collection = self.point_system.db_manager.db.user_points
            cursor = collection.find({})
            
            users = []
            async for doc in cursor:
                users.append(UserPoints(**doc))
            
            return users
        except Exception as e:
            logger.error(f"전체 사용자 포인트 조회 오류: {str(e)}")
            return []
    
    async def get_payment_statistics(self) -> Dict[str, Any]:
        """결제 통계 조회"""
        try:
            collection = self.point_system.db_manager.db.payment_transactions
            
            # 전체 통계
            total_payments = await collection.count_documents({})
            completed_payments = await collection.count_documents({"status": PaymentStatus.COMPLETED})
            total_revenue = 0
            
            # 수익 계산
            cursor = collection.find({"status": PaymentStatus.COMPLETED})
            async for doc in cursor:
                total_revenue += doc.get("amount", 0)
            
            return {
                "total_payments": total_payments,
                "completed_payments": completed_payments,
                "failed_payments": total_payments - completed_payments,
                "total_revenue": total_revenue,
                "success_rate": (completed_payments / total_payments * 100) if total_payments > 0 else 0
            }
        except Exception as e:
            logger.error(f"결제 통계 조회 오류: {str(e)}")
            return {}
    
    async def add_bonus_points(self, user_id: str, points: int, reason: str, admin_id: str) -> bool:
        """관리자가 보너스 포인트 지급"""
        return await self.point_system.add_points(
            user_id,
            points,
            f"관리자 보너스: {reason}",
            {"admin_id": admin_id, "type": "admin_bonus"}
        )
    
    async def create_custom_package(self, package: PointPackage) -> bool:
        """커스텀 포인트 패키지 생성"""
        try:
            # 기존 패키지에 추가
            self.point_system.packages.append(package)
            
            # 데이터베이스에 저장
            collection = self.point_system.db_manager.db.point_packages
            await collection.insert_one(package.dict())
            
            logger.info(f"커스텀 패키지 생성: {package.id}")
            return True
        except Exception as e:
            logger.error(f"커스텀 패키지 생성 오류: {str(e)}")
            return False 