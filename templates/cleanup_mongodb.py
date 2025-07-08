#!/usr/bin/env python3
"""
MongoDB 세션 데이터 정리 스크립트
null, undefined, 빈 문자열 세션 ID를 제거합니다.
"""

from pymongo import MongoClient
from datetime import datetime

def cleanup_mongodb_sessions():
    try:
        # MongoDB 연결
        client = MongoClient('mongodb://localhost:27017')
        db = client['eora_ai']
        
        print(f"🔗 MongoDB 연결 성공: {datetime.now()}")
        
        # 1. null session_id 삭제
        result1 = db.sessions.delete_many({'session_id': None})
        print(f"✅ null session_id 삭제 완료: {result1.deleted_count}개")
        
        # 2. undefined session_id 삭제
        result2 = db.sessions.delete_many({'session_id': 'undefined'})
        print(f"✅ undefined session_id 삭제 완료: {result2.deleted_count}개")
        
        # 3. null string session_id 삭제
        result3 = db.sessions.delete_many({'session_id': 'null'})
        print(f"✅ null string session_id 삭제 완료: {result3.deleted_count}개")
        
        # 4. 빈 문자열 session_id 삭제
        result4 = db.sessions.delete_many({'session_id': ''})
        print(f"✅ 빈 문자열 session_id 삭제 완료: {result4.deleted_count}개")
        
        # 5. chat_logs에서도 동일하게 정리
        result5 = db.chat_logs.delete_many({'session_id': None})
        print(f"✅ null session_id 메시지 삭제 완료: {result5.deleted_count}개")
        
        result6 = db.chat_logs.delete_many({'session_id': 'undefined'})
        print(f"✅ undefined session_id 메시지 삭제 완료: {result6.deleted_count}개")
        
        result7 = db.chat_logs.delete_many({'session_id': 'null'})
        print(f"✅ null string session_id 메시지 삭제 완료: {result7.deleted_count}개")
        
        result8 = db.chat_logs.delete_many({'session_id': ''})
        print(f"✅ 빈 문자열 session_id 메시지 삭제 완료: {result8.deleted_count}개")
        
        # 6. 남은 세션 수 확인
        remaining_sessions = db.sessions.count_documents({})
        remaining_messages = db.chat_logs.count_documents({})
        
        print(f"📊 정리 후 남은 세션 수: {remaining_sessions}개")
        print(f"📊 정리 후 남은 메시지 수: {remaining_messages}개")
        
        print(f"✅ MongoDB 정리 완료: {datetime.now()}")
        
    except Exception as e:
        print(f"❌ MongoDB 정리 오류: {e}")

if __name__ == "__main__":
    cleanup_mongodb_sessions() 