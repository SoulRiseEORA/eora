#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포인트 판매 수익 관리 시스템
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PointRevenueManager:
    """포인트 판매 수익 관리자"""
    
    def __init__(self):
        """포인트 수익 관리자 초기화"""
        load_dotenv()
        
        # 수익 데이터 파일
        self.revenue_file = "point_revenue_data.json"
        self.revenue_data = self._load_revenue_data()
        
        # 포인트 패키지 정의
        self.point_packages = {
            'basic': {
                'id': 'basic',
                'name': '기본 패키지',
                'points': 1000,
                'price': 10000,  # 10,000원
                'description': '1,000포인트 (10,000원)',
                'popular': False
            },
            'premium': {
                'id': 'premium',
                'name': '프리미엄 패키지',
                'points': 5000,
                'price': 45000,  # 45,000원 (10% 할인)
                'description': '5,000포인트 (45,000원) - 10% 할인',
                'popular': True
            },
            'unlimited': {
                'id': 'unlimited',
                'name': '무제한 패키지',
                'points': 10000,
                'price': 80000,  # 80,000원 (20% 할인)
                'description': '10,000포인트 (80,000원) - 20% 할인',
                'popular': False
            },
            'vip': {
                'id': 'vip',
                'name': 'VIP 패키지',
                'points': 20000,
                'price': 150000,  # 150,000원 (25% 할인)
                'description': '20,000포인트 (150,000원) - 25% 할인',
                'popular': False
            }
        }
        
        # 수수료 설정
        self.transaction_fee_rate = 0.05  # 5% 수수료
        self.minimum_fee = 1000  # 최소 수수료 1,000원
        
        logger.info("✅ 포인트 수익 관리자 초기화 완료")
    
    def _load_revenue_data(self) -> Dict[str, Any]:
        """수익 데이터 로드"""
        try:
            if os.path.exists(self.revenue_file):
                with open(self.revenue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # 초기 데이터 구조
            return {
                'total_revenue': 0,
                'total_transactions': 0,
                'total_points_sold': 0,
                'total_fees_collected': 0,
                'daily_revenue': {},
                'monthly_revenue': {},
                'transactions': [],
                'package_sales': {
                    'basic': {'count': 0, 'revenue': 0},
                    'premium': {'count': 0, 'revenue': 0},
                    'unlimited': {'count': 0, 'revenue': 0},
                    'vip': {'count': 0, 'revenue': 0}
                },
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 수익 데이터 로드 실패: {e}")
            return {}
    
    def _save_revenue_data(self):
        """수익 데이터 저장"""
        try:
            self.revenue_data['last_updated'] = datetime.now().isoformat()
            with open(self.revenue_file, 'w', encoding='utf-8') as f:
                json.dump(self.revenue_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 수익 데이터 저장 실패: {e}")
    
    def get_point_packages(self) -> List[Dict[str, Any]]:
        """포인트 패키지 목록 반환"""
        try:
            packages = []
            for package_id, package_info in self.point_packages.items():
                packages.append({
                    'id': package_id,
                    'name': package_info['name'],
                    'points': package_info['points'],
                    'price': package_info['price'],
                    'description': package_info['description'],
                    'popular': package_info['popular'],
                    'price_per_point': round(package_info['price'] / package_info['points'], 2)
                })
            
            # 가격순 정렬
            packages.sort(key=lambda x: x['price'])
            return packages
            
        except Exception as e:
            logger.error(f"❌ 포인트 패키지 조회 실패: {e}")
            return []
    
    def calculate_purchase_cost(self, package_id: str, payment_method: str = 'card') -> Dict[str, Any]:
        """포인트 구매 비용 계산"""
        try:
            if package_id not in self.point_packages:
                return {
                    'success': False,
                    'error': '존재하지 않는 패키지입니다.'
                }
            
            package = self.point_packages[package_id]
            base_price = package['price']
            
            # 수수료 계산
            transaction_fee = max(
                self.minimum_fee,
                int(base_price * self.transaction_fee_rate)
            )
            
            # 총 비용
            total_cost = base_price + transaction_fee
            
            # 할인율 계산
            original_price = package['points'] * 10  # 1포인트 = 10원 기준
            discount_rate = round((1 - base_price / original_price) * 100, 1)
            
            return {
                'success': True,
                'package_id': package_id,
                'package_name': package['name'],
                'points': package['points'],
                'base_price': base_price,
                'transaction_fee': transaction_fee,
                'total_cost': total_cost,
                'discount_rate': discount_rate,
                'price_per_point': round(base_price / package['points'], 2),
                'payment_method': payment_method
            }
            
        except Exception as e:
            logger.error(f"❌ 구매 비용 계산 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_point_purchase(self, user_id: str, package_id: str, payment_method: str = 'card', 
                             payment_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """포인트 구매 처리"""
        try:
            # 구매 비용 계산
            cost_info = self.calculate_purchase_cost(package_id, payment_method)
            if not cost_info['success']:
                return cost_info
            
            # 현재 시간
            now = datetime.now()
            transaction_id = f"TXN_{now.strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
            
            # 거래 정보 생성
            transaction = {
                'transaction_id': transaction_id,
                'user_id': user_id,
                'package_id': package_id,
                'package_name': cost_info['package_name'],
                'points': cost_info['points'],
                'base_price': cost_info['base_price'],
                'transaction_fee': cost_info['transaction_fee'],
                'total_cost': cost_info['total_cost'],
                'payment_method': payment_method,
                'payment_details': payment_details or {},
                'timestamp': now.isoformat(),
                'status': 'completed'
            }
            
            # 수익 데이터 업데이트
            self.revenue_data['total_revenue'] += cost_info['total_cost']
            self.revenue_data['total_transactions'] += 1
            self.revenue_data['total_points_sold'] += cost_info['points']
            self.revenue_data['total_fees_collected'] += cost_info['transaction_fee']
            
            # 일별 수익 업데이트
            date_key = now.strftime('%Y-%m-%d')
            if date_key not in self.revenue_data['daily_revenue']:
                self.revenue_data['daily_revenue'][date_key] = {
                    'revenue': 0,
                    'transactions': 0,
                    'points_sold': 0
                }
            
            self.revenue_data['daily_revenue'][date_key]['revenue'] += cost_info['total_cost']
            self.revenue_data['daily_revenue'][date_key]['transactions'] += 1
            self.revenue_data['daily_revenue'][date_key]['points_sold'] += cost_info['points']
            
            # 월별 수익 업데이트
            month_key = now.strftime('%Y-%m')
            if month_key not in self.revenue_data['monthly_revenue']:
                self.revenue_data['monthly_revenue'][month_key] = {
                    'revenue': 0,
                    'transactions': 0,
                    'points_sold': 0
                }
            
            self.revenue_data['monthly_revenue'][month_key]['revenue'] += cost_info['total_cost']
            self.revenue_data['monthly_revenue'][month_key]['transactions'] += 1
            self.revenue_data['monthly_revenue'][month_key]['points_sold'] += cost_info['points']
            
            # 패키지별 판매 통계 업데이트
            if package_id in self.revenue_data['package_sales']:
                self.revenue_data['package_sales'][package_id]['count'] += 1
                self.revenue_data['package_sales'][package_id]['revenue'] += cost_info['total_cost']
            
            # 거래 기록 추가
            self.revenue_data['transactions'].append(transaction)
            
            # 데이터 저장
            self._save_revenue_data()
            
            logger.info(f"✅ 포인트 구매 처리 완료: {user_id} -> {package_id} ({cost_info['points']}포인트)")
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'points_added': cost_info['points'],
                'total_cost': cost_info['total_cost'],
                'message': f"{cost_info['points']}포인트가 성공적으로 구매되었습니다."
            }
            
        except Exception as e:
            logger.error(f"❌ 포인트 구매 처리 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '포인트 구매 처리 중 오류가 발생했습니다.'
            }
    
    def get_revenue_statistics(self, period: str = 'all') -> Dict[str, Any]:
        """수익 통계 조회"""
        try:
            stats = {
                'total_revenue': self.revenue_data.get('total_revenue', 0),
                'total_transactions': self.revenue_data.get('total_transactions', 0),
                'total_points_sold': self.revenue_data.get('total_points_sold', 0),
                'total_fees_collected': self.revenue_data.get('total_fees_collected', 0),
                'average_transaction_value': 0,
                'package_sales': self.revenue_data.get('package_sales', {}),
                'period': period
            }
            
            # 평균 거래 금액 계산
            if stats['total_transactions'] > 0:
                stats['average_transaction_value'] = round(
                    stats['total_revenue'] / stats['total_transactions']
                )
            
            # 기간별 통계
            if period == 'today':
                today = datetime.now().strftime('%Y-%m-%d')
                daily_data = self.revenue_data.get('daily_revenue', {}).get(today, {})
                stats.update({
                    'period_revenue': daily_data.get('revenue', 0),
                    'period_transactions': daily_data.get('transactions', 0),
                    'period_points_sold': daily_data.get('points_sold', 0)
                })
            elif period == 'month':
                this_month = datetime.now().strftime('%Y-%m')
                monthly_data = self.revenue_data.get('monthly_revenue', {}).get(this_month, {})
                stats.update({
                    'period_revenue': monthly_data.get('revenue', 0),
                    'period_transactions': monthly_data.get('transactions', 0),
                    'period_points_sold': monthly_data.get('points_sold', 0)
                })
            else:  # all
                stats.update({
                    'period_revenue': stats['total_revenue'],
                    'period_transactions': stats['total_transactions'],
                    'period_points_sold': stats['total_points_sold']
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 수익 통계 조회 실패: {e}")
            return {
                'error': str(e),
                'period': period
            }
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 거래 내역 조회"""
        try:
            transactions = self.revenue_data.get('transactions', [])
            # 최신 순으로 정렬
            sorted_transactions = sorted(
                transactions, 
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
            
            return sorted_transactions[:limit]
            
        except Exception as e:
            logger.error(f"❌ 최근 거래 내역 조회 실패: {e}")
            return []
    
    def get_daily_revenue_chart_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """일별 수익 차트 데이터"""
        try:
            chart_data = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime('%Y-%m-%d')
                daily_data = self.revenue_data.get('daily_revenue', {}).get(date_key, {})
                
                chart_data.append({
                    'date': date_key,
                    'revenue': daily_data.get('revenue', 0),
                    'transactions': daily_data.get('transactions', 0),
                    'points_sold': daily_data.get('points_sold', 0)
                })
                
                current_date += timedelta(days=1)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"❌ 일별 수익 차트 데이터 조회 실패: {e}")
            return []
    
    def refund_transaction(self, transaction_id: str, reason: str = "고객 요청") -> Dict[str, Any]:
        """거래 환불 처리"""
        try:
            # 거래 찾기
            transaction = None
            for txn in self.revenue_data.get('transactions', []):
                if txn.get('transaction_id') == transaction_id:
                    transaction = txn
                    break
            
            if not transaction:
                return {
                    'success': False,
                    'error': '거래를 찾을 수 없습니다.'
                }
            
            if transaction.get('status') == 'refunded':
                return {
                    'success': False,
                    'error': '이미 환불된 거래입니다.'
                }
            
            # 환불 처리
            refund_amount = transaction['total_cost']
            
            # 수익 데이터에서 차감
            self.revenue_data['total_revenue'] -= refund_amount
            self.revenue_data['total_fees_collected'] -= transaction['transaction_fee']
            self.revenue_data['total_points_sold'] -= transaction['points']
            
            # 거래 상태 업데이트
            transaction['status'] = 'refunded'
            transaction['refund_reason'] = reason
            transaction['refund_timestamp'] = datetime.now().isoformat()
            
            # 환불 거래 기록
            refund_transaction = {
                'transaction_id': f"REFUND_{transaction_id}",
                'original_transaction_id': transaction_id,
                'user_id': transaction['user_id'],
                'refund_amount': refund_amount,
                'refund_reason': reason,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            self.revenue_data['transactions'].append(refund_transaction)
            
            # 데이터 저장
            self._save_revenue_data()
            
            logger.info(f"✅ 거래 환불 완료: {transaction_id} -> {refund_amount}원")
            
            return {
                'success': True,
                'refund_amount': refund_amount,
                'message': '환불이 성공적으로 처리되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"❌ 거래 환불 처리 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '환불 처리 중 오류가 발생했습니다.'
            }

# 전역 인스턴스
revenue_manager = PointRevenueManager()

def get_revenue_manager() -> PointRevenueManager:
    """수익 관리자 인스턴스 반환"""
    return revenue_manager 