#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')

def test_mongodb():
    """MongoDB 직접 확인"""
    try:
        import pymongo
        
        print("🔍 MongoDB 데이터 직접 확인 중...")
        print("=" * 50)
        
        # MongoDB 연결
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["eora_ai"]
        
        print("✅ MongoDB 연결 성공!")
        
        # 컬렉션 목록
        collections = db.list_collection_names()
        print(f"📋 전체 컬렉션: {len(collections)}개")
        
        # memories 컬렉션 확인
        if 'memories' in collections:
            memories_col = db['memories']
            
            # 총 개수
            total_count = memories_col.count_documents({})
            print(f"💾 총 메모리: {total_count:,}개")
            
            # 학습 자료 개수
            learning_count = memories_col.count_documents({"memory_type": "learning_material"})
            print(f"📚 학습 자료: {learning_count:,}개")
            
            # 최신 5개 샘플
            print("\n📝 최신 메모리 5개 샘플:")
            for i, doc in enumerate(memories_col.find().sort("timestamp", -1).limit(5), 1):
                content = doc.get('content', '')[:100]
                source = doc.get('source_file', 'unknown')
                print(f"  {i}. [{source}] {content}...")
            
            # 키워드 검색 테스트
            print("\n🔍 키워드 검색 테스트:")
            search_terms = ["금강", "상담", "영업시간"]
            
            for term in search_terms:
                count = memories_col.count_documents({
                    "$or": [
                        {"content": {"$regex": term, "$options": "i"}},
                        {"response": {"$regex": term, "$options": "i"}},
                        {"tags": term}
                    ]
                })
                print(f"   '{term}': {count}개")
        else:
            print("❌ memories 컬렉션이 없습니다!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB 테스트 실패: {e}")

def test_server():
    """서버 API 테스트"""
    try:
        import requests
        
        print("\n🌐 서버 API 테스트...")
        print("=" * 30)
        
        base_url = "http://127.0.0.1:8002"
        
        # 헬스 체크
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            print(f"✅ 서버 상태: {response.status_code}")
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return
        
        # 메모리 통계
        try:
            response = requests.get(f"{base_url}/api/aura/memory/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"📊 API 메모리 통계: {data}")
            else:
                print(f"⚠️ 통계 API 응답: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 통계 API 오류: {e}")
        
        # 검색 테스트
        try:
            response = requests.get(f"{base_url}/api/aura/recall", 
                                  params={"query": "금강", "recall_type": "normal"}, 
                                  timeout=10)
            if response.status_code == 200:
                data = response.json()
                memories = data.get('memories', [])
                print(f"🔍 '금강' 검색 결과: {len(memories)}개")
            else:
                print(f"⚠️ 검색 API 응답: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 검색 API 오류: {e}")
            
    except ImportError:
        print("⚠️ requests 모듈이 없습니다.")

if __name__ == "__main__":
    test_mongodb()
    test_server()
    
    print("\n" + "=" * 50)
    print("🎯 검증 완료!")
    print("=" * 50) 