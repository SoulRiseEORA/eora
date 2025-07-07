#!/usr/bin/env python3
"""
최종 배포 전 검증 스크립트
"""

import os
import sys
import importlib
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트"""
    print("🔍 모듈 import 테스트...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'pymongo',
        'redis',
        'openai',
        'jwt',
        'passlib',
        'jinja2',
        'python-dotenv'
    ]
    
    optional_modules = [
        'faiss',
        'sentence_transformers',
        'torch',
        'transformers'
    ]
    
    # 필수 모듈 테스트
    failed_modules = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_modules.append(module)
    
    # 선택적 모듈 테스트
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} (선택적)")
        except ImportError:
            print(f"⚠️ {module} (선택적, 누락됨)")
    
    return len(failed_modules) == 0

def check_files():
    """필요한 파일들이 존재하는지 테스트"""
    print("\n📁 파일 존재 테스트...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'railway.json'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_templates():
    """템플릿 파일들이 존재하는지 테스트"""
    print("\n🎨 템플릿 파일 테스트...")
    
    template_files = [
        'home.html',
        'chat.html',
        'test_chat_simple.html'
    ]
    
    templates_dir = Path('templates')
    if not templates_dir.exists():
        print("❌ templates 디렉토리가 없습니다")
        return False
    
    missing_templates = []
    for template in template_files:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"✅ {template}")
        else:
            print(f"⚠️ {template} (누락됨)")
            missing_templates.append(template)
    
    return len(missing_templates) == 0

def check_main_app():
    """main.py 앱이 정상적으로 로드되는지 테스트"""
    print("\n🚀 메인 앱 로드 테스트...")
    
    try:
        # main.py를 모듈로 import
        sys.path.insert(0, str(Path.cwd()))
        import main
        
        # FastAPI 앱 객체 확인
        if hasattr(main, 'app'):
            print("✅ FastAPI 앱 객체 생성 성공")
        else:
            print("❌ FastAPI 앱 객체가 없습니다")
            return False
        
        # 헬스체크 엔드포인트 확인
        routes = [route.path for route in main.app.routes]
        if '/health' in routes:
            print("✅ 헬스체크 엔드포인트 존재")
        else:
            print("❌ 헬스체크 엔드포인트가 없습니다")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 메인 앱 로드 실패: {e}")
        return False

def check_environment():
    """환경변수 설정 테스트"""
    print("\n🌍 환경변수 테스트...")
    
    # 필수 환경변수는 아니지만 확인
    env_vars = [
        'OPENAI_API_KEY',
        'MONGODB_URL',
        'REDIS_URL',
        'JWT_SECRET'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} 설정됨")
        else:
            print(f"⚠️ {var} 설정되지 않음 (선택적)")
    
    return True

def check_railway_config():
    """Railway 설정 파일 확인"""
    print("\n🚂 Railway 설정 테스트...")
    
    try:
        import json
        with open('railway.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['build', 'deploy']
        for key in required_keys:
            if key in config:
                print(f"✅ {key} 설정 존재")
            else:
                print(f"❌ {key} 설정 누락")
                return False
        
        # 시작 명령어 확인
        start_cmd = config.get('deploy', {}).get('startCommand')
        if start_cmd == 'python main.py':
            print("✅ 시작 명령어 올바름")
        else:
            print(f"⚠️ 시작 명령어: {start_cmd}")
        
        return True
        
    except Exception as e:
        print(f"❌ Railway 설정 확인 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 EORA AI System 최종 배포 전 검증")
    print("=" * 50)
    
    tests = [
        ("모듈 Import", check_imports),
        ("파일 존재", check_files),
        ("템플릿 파일", check_templates),
        ("메인 앱 로드", check_main_app),
        ("환경변수", check_environment),
        ("Railway 설정", check_railway_config)
    ]
    
    passed = 0
    total = len(tests)
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 통과")
        else:
            print(f"❌ {test_name} 실패")
            failed_tests.append(test_name)
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 통과했습니다!")
        print("✅ Railway 배포 준비가 완료되었습니다.")
        print("\n🚀 배포 명령어:")
        print("   .\\deploy.bat")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        print("🔧 실패한 테스트:")
        for test in failed_tests:
            print(f"   - {test}")
        print("\n💡 문제를 해결한 후 다시 테스트해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 