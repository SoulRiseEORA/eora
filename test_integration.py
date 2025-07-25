#!/usr/bin/env python3
"""
EORA AI System - 통합 테스트
app_fixed.py와 app.py 통합 검증
"""

import sys
import os
import json
import subprocess
import time

def test_imports():
    """모듈 import 테스트"""
    print("🔍 모듈 import 테스트...")
    
    try:
        # src 디렉토리를 Python 경로에 추가
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)
        
        # 필수 모듈들 import 테스트
        import fastapi
        print("✅ FastAPI import 성공")
        
        import uvicorn
        print("✅ Uvicorn import 성공")
        
        import pymongo
        print("✅ PyMongo import 성공")
        
        import openai
        print("✅ OpenAI import 성공")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import 오류: {e}")
        return False

def test_app_structure():
    """app.py 구조 테스트"""
    print("\n🔍 app.py 구조 테스트...")
    
    try:
        import app
        
        # FastAPI app 객체 확인
        if hasattr(app, 'app'):
            print("✅ FastAPI app 객체 발견")
        else:
            print("❌ FastAPI app 객체 없음")
            return False
        
        # 주요 함수들 확인
        required_functions = [
            'create_indexes',
            'load_prompts_data',
            'init_mongodb',
            'init_openai_client'
        ]
        
        for func_name in required_functions:
            if hasattr(app, func_name):
                print(f"✅ {func_name} 함수 발견")
            else:
                print(f"❌ {func_name} 함수 없음")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ app.py 구조 테스트 실패: {e}")
        return False

def test_mongodb_boolean_fix():
    """MongoDB boolean check 수정 테스트"""
    print("\n🔍 MongoDB boolean check 수정 테스트...")
    
    try:
        # app.py 파일에서 boolean check 패턴 확인
        with open('src/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 잘못된 패턴 확인
        if 'if not db:' in content:
            print("❌ 아직 잘못된 boolean check 패턴 발견")
            return False
        
        # 올바른 패턴 확인
        if 'if db is None:' in content:
            print("✅ 올바른 boolean check 패턴 발견")
        else:
            print("⚠️ boolean check 패턴을 찾을 수 없음")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB boolean check 테스트 실패: {e}")
        return False

def test_requirements():
    """requirements.txt 테스트"""
    print("\n🔍 requirements.txt 테스트...")
    
    try:
        with open('src/requirements.txt', 'r') as f:
            requirements = f.read()
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'openai',
            'pymongo',
            'python-dotenv'
        ]
        
        for package in required_packages:
            if package in requirements:
                print(f"✅ {package} 패키지 발견")
            else:
                print(f"❌ {package} 패키지 없음")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ requirements.txt 테스트 실패: {e}")
        return False

def test_start_scripts():
    """시작 스크립트 테스트"""
    print("\n🔍 시작 스크립트 테스트...")
    
    scripts = ['start_app.ps1', 'start_app.bat']
    
    for script in scripts:
        if os.path.exists(script):
            print(f"✅ {script} 파일 발견")
        else:
            print(f"❌ {script} 파일 없음")
            return False
    
    return True

def main():
    """메인 테스트 함수"""
    print("🚀 EORA AI System - 통합 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("모듈 Import", test_imports),
        ("app.py 구조", test_app_structure),
        ("MongoDB Boolean Fix", test_mongodb_boolean_fix),
        ("Requirements", test_requirements),
        ("시작 스크립트", test_start_scripts)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트...")
        if test_func():
            print(f"✅ {test_name} 테스트 통과")
            passed += 1
        else:
            print(f"❌ {test_name} 테스트 실패")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 통합이 성공적으로 완료되었습니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패. 추가 수정이 필요합니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 