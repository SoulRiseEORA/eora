#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 세션 시스템 진단 및 수정 스크립트
채팅 세션 관련 문제를 진단하고 수정합니다.
"""

import os
import sys
import logging
import datetime
import requests
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 서버 URL 설정
BASE_URL = "http://localhost:8001"

def test_session_api():
    """세션 API가 제대로 작동하는지 테스트합니다."""
    logger.info("🔍 세션 API 테스트 시작...")
    
    # 1. 새 세션 생성 테스트
    try:
        logger.info("1️⃣ 새 세션 생성 테스트...")
        response = requests.post(
            f"{BASE_URL}/api/sessions", 
            json={"name": f"테스트 세션 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "user_id": "test_user"}
        )
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get("_id")
            logger.info(f"✅ 세션 생성 성공! 세션 ID: {session_id}")
            
            # 2. 세션 목록 조회 테스트
            logger.info("2️⃣ 세션 목록 조회 테스트...")
            response = requests.get(f"{BASE_URL}/api/sessions")
            
            if response.status_code == 200:
                sessions_data = response.json()
                sessions = sessions_data.get("sessions", [])
                logger.info(f"✅ 세션 목록 조회 성공! {len(sessions)}개의 세션이 있습니다.")
                
                # 3. 세션 메시지 저장 테스트
                if sessions and len(sessions) > 0:
                    test_session_id = sessions[0]["id"]
                    logger.info(f"3️⃣ 세션 메시지 저장 테스트... (세션 ID: {test_session_id})")
                    
                    # 사용자 메시지 저장
                    message_data = {
                        "session_id": test_session_id,
                        "user_id": "test_user",
                        "content": "안녕하세요, 테스트 메시지입니다.",
                        "role": "user"
                    }
                    
                    response = requests.post(f"{BASE_URL}/api/messages", json=message_data)
                    
                    if response.status_code == 200:
                        logger.info("✅ 메시지 저장 성공!")
                        
                        # 4. 세션 메시지 조회 테스트
                        logger.info(f"4️⃣ 세션 메시지 조회 테스트... (세션 ID: {test_session_id})")
                        response = requests.get(f"{BASE_URL}/api/sessions/{test_session_id}/messages")
                        
                        if response.status_code == 200:
                            messages_data = response.json()
                            messages = messages_data.get("messages", [])
                            logger.info(f"✅ 메시지 조회 성공! {len(messages)}개의 메시지가 있습니다.")
                            
                            # 성공한 경우 몇 개의 메시지가 있는지 출력
                            for i, msg in enumerate(messages):
                                logger.info(f"   메시지 {i+1}: [{msg.get('role', 'unknown')}] {msg.get('content', '')[:50]}...")
                            
                            # 5. 채팅 API 테스트
                            logger.info(f"5️⃣ 채팅 API 테스트... (세션 ID: {test_session_id})")
                            chat_data = {
                                "message": "테스트 채팅 메시지입니다.",
                                "session_id": test_session_id
                            }
                            
                            response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
                            
                            if response.status_code == 200:
                                chat_response = response.json()
                                logger.info(f"✅ 채팅 API 응답 성공!")
                                logger.info(f"   응답: {chat_response.get('response', '')[:50]}...")
                            else:
                                logger.error(f"❌ 채팅 API 응답 실패: {response.status_code} - {response.text}")
                        else:
                            logger.error(f"❌ 메시지 조회 실패: {response.status_code} - {response.text}")
                    else:
                        logger.error(f"❌ 메시지 저장 실패: {response.status_code} - {response.text}")
                else:
                    logger.warning("⚠️ 세션이 없어 메시지 테스트를 건너뜁니다.")
            else:
                logger.error(f"❌ 세션 목록 조회 실패: {response.status_code} - {response.text}")
        else:
            logger.error(f"❌ 세션 생성 실패: {response.status_code} - {response.text}")
    
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
    
    logger.info("🏁 세션 API 테스트 완료")

def check_database_connection():
    """데이터베이스 연결 상태를 확인합니다."""
    logger.info("🔍 데이터베이스 연결 상태 확인...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        
        if response.status_code == 200:
            status_data = response.json()
            db_status = status_data.get("database", {}).get("status", "unknown")
            logger.info(f"✅ 데이터베이스 상태: {db_status}")
            return db_status == "connected"
        else:
            logger.error(f"❌ 서버 상태 조회 실패: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ 서버 상태 확인 중 오류 발생: {str(e)}")
        return False

def main():
    """메인 함수"""
    logger.info("🚀 EORA AI 세션 시스템 진단 시작")
    
    # 1. 서버 접속 가능 여부 확인
    try:
        # 간단하게 서버 접속만 확인
        requests.get(f"{BASE_URL}/")
        logger.info("✅ 서버 접속 시도")
    except Exception as e:
        logger.error(f"❌ 서버 접속 실패: {str(e)}")
        logger.info("💡 서버가 실행 중인지 확인하고 다시 시도해주세요.")
        return
    
    # 2. 세션 API 테스트
    test_session_api()
    
    logger.info("🏁 EORA AI 세션 시스템 진단 완료")

if __name__ == "__main__":
    main() 