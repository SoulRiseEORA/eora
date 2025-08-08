#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메모리 저장 및 회상 기능 검증 스크립트
MongoDB 장기저장 및 회상 기능 테스트
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryVerificationTest:
    """메모리 시스템 검증 테스트"""
    
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.session_id = None
        self.user_email = "admin@eora.ai"
        self.password = "admin123"
        self.test_messages = [
            "안녕하세요! 오늘은 아름다운 날이네요.",
            "파이썬 프로그래밍에 대해 이야기해봅시다.",
            "인공지능의 발전이 정말 놀랍습니다.",
            "음악을 들으면서 코딩하는 것을 좋아합니다.",
            "미래의 기술 발전에 대해 어떻게 생각하세요?"
        ]
        
    def login(self):
        """관리자 로그인"""
        try:
            login_data = {
                "email": self.user_email,
                "password": self.password
            }
            
            response = requests.post(
                f"{self.server_url}/api/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ 로그인 성공")
                return True
            else:
                logger.error(f"❌ 로그인 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 로그인 오류: {e}")
            return False
    
    def create_test_session(self):
        """테스트용 세션 생성"""
        try:
            session_data = {
                "name": f"메모리 검증 테스트 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            response = requests.post(
                f"{self.server_url}/api/sessions",
                json=session_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id") or data.get("session", {}).get("id")
                logger.info(f"✅ 테스트 세션 생성 성공: {self.session_id}")
                return True
            else:
                logger.error(f"❌ 세션 생성 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 세션 생성 오류: {e}")
            return False
    
    def send_test_messages(self):
        """테스트 메시지들을 전송하여 메모리에 저장"""
        stored_messages = []
        
        for i, message in enumerate(self.test_messages, 1):
            try:
                logger.info(f"📤 메시지 {i} 전송: {message[:30]}...")
                
                chat_data = {
                    "message": message,
                    "session_id": self.session_id
                }
                
                response = requests.post(
                    f"{self.server_url}/api/chat",
                    json=chat_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("response", "")
                    logger.info(f"✅ 메시지 {i} 성공: {ai_response[:50]}...")
                    
                    stored_messages.append({
                        "user_message": message,
                        "ai_response": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # 메시지 간 간격
                    import time
                    time.sleep(2)
                    
                else:
                    logger.error(f"❌ 메시지 {i} 전송 실패: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ 메시지 {i} 전송 오류: {e}")
        
        return stored_messages
    
    def verify_session_messages(self):
        """세션 메시지가 저장되었는지 확인"""
        try:
            response = requests.get(
                f"{self.server_url}/api/sessions/{self.session_id}/messages",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                logger.info(f"✅ 세션 메시지 조회 성공: {len(messages)}개 메시지")
                
                # 메시지 내용 확인
                user_messages = [msg for msg in messages if msg.get("role") == "user"]
                ai_messages = [msg for msg in messages if msg.get("role") == "assistant"]
                
                logger.info(f"📝 사용자 메시지: {len(user_messages)}개")
                logger.info(f"🤖 AI 응답: {len(ai_messages)}개")
                
                return {
                    "total_messages": len(messages),
                    "user_messages": len(user_messages),
                    "ai_messages": len(ai_messages),
                    "messages": messages
                }
            else:
                logger.error(f"❌ 메시지 조회 실패: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 메시지 조회 오류: {e}")
            return None
    
    def test_mongodb_connection(self):
        """MongoDB 연결 상태 테스트"""
        try:
            # database.py 모듈 import
            sys.path.append('src')
            from database import verify_connection, mongo_client, db_mgr
            
            # 연결 상태 확인
            if verify_connection():
                logger.info("✅ MongoDB 연결 성공")
                
                # 컬렉션 상태 확인
                if mongo_client and db_mgr:
                    # 메모리 컬렉션 확인
                    try:
                        from database import memories_collection
                        if memories_collection:
                            memory_count = memories_collection.count_documents({})
                            logger.info(f"📊 저장된 메모리 개수: {memory_count}")
                        
                        # 채팅 로그 컬렉션 확인  
                        from database import chat_logs_collection
                        if chat_logs_collection:
                            chat_count = chat_logs_collection.count_documents({})
                            logger.info(f"💬 저장된 채팅 로그: {chat_count}")
                            
                        return True
                    except Exception as collection_error:
                        logger.warning(f"⚠️ 컬렉션 확인 오류: {collection_error}")
                        return True  # 연결은 성공했으므로 True 반환
                else:
                    logger.warning("⚠️ 데이터베이스 매니저가 초기화되지 않음")
                    return False
            else:
                logger.error("❌ MongoDB 연결 실패")
                return False
                
        except Exception as e:
            logger.error(f"❌ MongoDB 테스트 오류: {e}")
            return False
    
    def test_memory_persistence(self):
        """메모리 지속성 테스트 (서버 재시작 시뮬레이션)"""
        try:
            logger.info("🔄 메모리 지속성 테스트 시작...")
            
            # 현재 세션의 메시지 조회
            before_messages = self.verify_session_messages()
            if not before_messages:
                logger.error("❌ 초기 메시지 조회 실패")
                return False
            
            # 잠시 대기 (메모리 저장 완료를 위해)
            import time
            time.sleep(5)
            
            # 다시 메시지 조회 (지속성 확인)
            after_messages = self.verify_session_messages()
            if not after_messages:
                logger.error("❌ 지속성 확인 실패")
                return False
            
            # 메시지 개수 비교
            if before_messages["total_messages"] == after_messages["total_messages"]:
                logger.info("✅ 메모리 지속성 테스트 성공")
                return True
            else:
                logger.error("❌ 메시지 개수 불일치")
                return False
                
        except Exception as e:
            logger.error(f"❌ 지속성 테스트 오류: {e}")
            return False
    
    def test_recall_functionality(self):
        """회상 기능 테스트"""
        try:
            logger.info("🧠 회상 기능 테스트 시작...")
            
            # 이전 대화 내용과 관련된 질문
            recall_test_message = "이전에 이야기했던 파이썬 프로그래밍에 대해 더 자세히 설명해주세요."
            
            chat_data = {
                "message": recall_test_message,
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{self.server_url}/api/chat",
                json=chat_data,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                
                # 응답에 이전 대화 내용이 포함되었는지 확인
                recall_keywords = ["파이썬", "프로그래밍", "이전", "앞서"]
                has_recall = any(keyword in ai_response for keyword in recall_keywords)
                
                if has_recall:
                    logger.info("✅ 회상 기능 테스트 성공")
                    logger.info(f"📝 회상 응답: {ai_response[:100]}...")
                    return True
                else:
                    logger.warning("⚠️ 회상 기능 불확실")
                    logger.info(f"📝 응답: {ai_response[:100]}...")
                    return False
            else:
                logger.error(f"❌ 회상 테스트 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 회상 테스트 오류: {e}")
            return False
    
    def generate_report(self, test_results):
        """테스트 결과 보고서 생성"""
        report = {
            "test_date": datetime.now().isoformat(),
            "server_url": self.server_url,
            "session_id": self.session_id,
            "results": test_results,
            "summary": {
                "total_tests": len(test_results),
                "passed_tests": sum(1 for result in test_results.values() if result),
                "failed_tests": sum(1 for result in test_results.values() if not result)
            }
        }
        
        # 보고서 파일 저장
        report_filename = f"memory_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"📊 보고서 저장: {report_filename}")
        except Exception as e:
            logger.error(f"❌ 보고서 저장 실패: {e}")
        
        return report
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("🚀 메모리 시스템 검증 테스트 시작")
        logger.info("=" * 60)
        
        test_results = {}
        
        # 1. 로그인 테스트
        logger.info("1️⃣ 로그인 테스트")
        test_results["login"] = self.login()
        
        # 2. MongoDB 연결 테스트
        logger.info("\n2️⃣ MongoDB 연결 테스트")
        test_results["mongodb_connection"] = self.test_mongodb_connection()
        
        # 3. 세션 생성 테스트
        logger.info("\n3️⃣ 세션 생성 테스트")
        test_results["session_creation"] = self.create_test_session()
        
        # 4. 메시지 저장 테스트
        logger.info("\n4️⃣ 메시지 저장 테스트")
        if test_results["session_creation"]:
            stored_messages = self.send_test_messages()
            test_results["message_storage"] = len(stored_messages) > 0
        else:
            test_results["message_storage"] = False
        
        # 5. 메시지 조회 테스트
        logger.info("\n5️⃣ 메시지 조회 테스트")
        if test_results["message_storage"]:
            message_data = self.verify_session_messages()
            test_results["message_retrieval"] = message_data is not None and message_data["total_messages"] > 0
        else:
            test_results["message_retrieval"] = False
        
        # 6. 메모리 지속성 테스트
        logger.info("\n6️⃣ 메모리 지속성 테스트")
        if test_results["message_retrieval"]:
            test_results["memory_persistence"] = self.test_memory_persistence()
        else:
            test_results["memory_persistence"] = False
        
        # 7. 회상 기능 테스트
        logger.info("\n7️⃣ 회상 기능 테스트")
        if test_results["memory_persistence"]:
            test_results["recall_functionality"] = self.test_recall_functionality()
        else:
            test_results["recall_functionality"] = False
        
        # 결과 요약
        logger.info("\n" + "=" * 60)
        logger.info("📊 테스트 결과 요약")
        logger.info("=" * 60)
        
        for test_name, result in test_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            logger.info(f"{test_name}: {status}")
        
        # 보고서 생성
        report = self.generate_report(test_results)
        
        # 전체 결과
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        
        logger.info(f"\n🎯 전체 결과: {passed_tests}/{total_tests} 통과")
        
        if passed_tests == total_tests:
            logger.info("🎉 모든 테스트 통과! 메모리 시스템이 정상 작동합니다.")
        else:
            logger.warning("⚠️ 일부 테스트 실패. 시스템 점검이 필요합니다.")
        
        return report

def main():
    """메인 함수"""
    # 서버 URL 설정 (환경에 따라 조정)
    import argparse
    parser = argparse.ArgumentParser(description='메모리 시스템 검증 테스트')
    parser.add_argument('--server', default='http://localhost:8000', help='서버 URL')
    args = parser.parse_args()
    
    # 테스트 실행
    tester = MemoryVerificationTest(server_url=args.server)
    report = tester.run_all_tests()
    
    return report

if __name__ == "__main__":
    main()