#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서버 시작 문제 진단 스크립트
"""

import sys
import os

def test_imports():
    """필요한 모듈 import 테스트"""
    print("📦 모듈 import 테스트 시작")
    
    try:
        print("   FastAPI...", end=" ")
        from fastapi import FastAPI
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        return False
    
    try:
        print("   database 모듈...", end=" ")
        sys.path.append('src')
        import database
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        return False
        
    try:
        print("   app 모듈...", end=" ")
        import app
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        print(f"   상세 오류: {str(e)}")
        return False
    
    return True

def test_basic_server():
    """기본 서버 시작 테스트"""
    print("\n🚀 기본 서버 시작 테스트")
    
    try:
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"message": "Hello World"}
        
        print("✅ 기본 FastAPI 앱 생성 성공")
        return True
        
    except Exception as e:
        print(f"❌ 기본 서버 생성 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔍 서버 시작 문제 진단")
    print("=" * 50)
    
    # Python 버전 확인
    print(f"🐍 Python 버전: {sys.version}")
    print(f"📁 현재 경로: {os.getcwd()}")
    
    # 모듈 import 테스트
    if test_imports():
        print("\n✅ 모든 모듈 import 성공")
    else:
        print("\n❌ 모듈 import 실패")
        sys.exit(1)
    
    # 기본 서버 테스트
    if test_basic_server():
        print("\n✅ 기본 서버 생성 성공")
    else:
        print("\n❌ 기본 서버 생성 실패")
        sys.exit(1)
    
    print("\n✅ 서버 시작 준비 완료!")
    print("💡 src/app.py를 직접 실행해보세요.") 