#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway 배포 전 최종 검증 및 배포 스크립트
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_git_status():
    """Git 상태 확인"""
    print("🔍 Git 상태 확인 중...")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("📝 변경된 파일이 있습니다:")
            print(result.stdout)
            return True
        else:
            print("✅ 모든 파일이 커밋되었습니다.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 상태 확인 실패: {e}")
        return False

def check_required_files():
    """필수 파일 존재 확인"""
    print("\n📁 필수 파일 확인 중...")
    required_files = [
        'railway_optimized.py',
        'requirements.txt',
        'railway.json',
        'nixpacks.toml',
        'Procfile',
        'RAILWAY_ENV_SETUP.md'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} 없음")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 누락된 파일: {missing_files}")
        return False
    
    print("✅ 모든 필수 파일 존재")
    return True

def check_railway_config():
    """Railway 설정 확인"""
    print("\n⚙️ Railway 설정 확인 중...")
    
    # railway.json 확인
    try:
        with open('railway.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'deploy' in config and 'startCommand' in config['deploy']:
            start_cmd = config['deploy']['startCommand']
            if 'railway_optimized.py' in start_cmd:
                print(f"✅ Railway startCommand: {start_cmd}")
            else:
                print(f"❌ 잘못된 startCommand: {start_cmd}")
                return False
        else:
            print("❌ railway.json에 startCommand 없음")
            return False
            
    except Exception as e:
        print(f"❌ railway.json 파싱 실패: {e}")
        return False
    
    # nixpacks.toml 확인
    if Path('nixpacks.toml').exists():
        print("✅ nixpacks.toml 존재")
    else:
        print("❌ nixpacks.toml 없음")
        return False
    
    print("✅ Railway 설정 완료")
    return True

def git_add_commit_push():
    """Git add, commit, push 실행"""
    print("\n🚀 Git 배포 시작...")
    
    try:
        # Git add
        print("📦 Git add...")
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Git add 완료")
        
        # Git commit
        print("💾 Git commit...")
        commit_message = "Railway 완전 최적화 및 모든 오류/경고 해결"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print("✅ Git commit 완료")
        
        # Git push
        print("📤 Git push...")
        subprocess.run(['git', 'push'], check=True)
        print("✅ Git push 완료")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 작업 실패: {e}")
        return False

def show_next_steps():
    """다음 단계 안내"""
    print("\n" + "="*60)
    print("🎉 배포 완료! 다음 단계를 진행하세요:")
    print("="*60)
    
    print("\n1. Railway 대시보드에서 환경변수 설정:")
    print("   - OPENAI_API_KEY=sk-your-api-key")
    print("   - DATABASE_NAME=eora_ai")
    print("   - PORT=8000")
    
    print("\n2. Railway 플러그인 추가:")
    print("   - MongoDB 플러그인 추가")
    print("   - Redis 플러그인 추가 (선택사항)")
    
    print("\n3. 배포 확인:")
    print("   - Railway 대시보드에서 배포 상태 확인")
    print("   - 로그에서 오류 메시지 확인")
    print("   - https://your-app.railway.app/health 접속")
    
    print("\n4. 문제 발생 시:")
    print("   - RAILWAY_ENV_SETUP.md 파일 참조")
    print("   - Railway 로그 확인")
    print("   - 환경변수 재설정")

def main():
    """메인 함수"""
    print("🚀 Railway 배포 전 최종 검증 및 배포")
    print("="*60)
    
    # 1. 필수 파일 확인
    if not check_required_files():
        print("\n❌ 필수 파일이 누락되었습니다. 배포를 중단합니다.")
        return False
    
    # 2. Railway 설정 확인
    if not check_railway_config():
        print("\n❌ Railway 설정에 문제가 있습니다. 배포를 중단합니다.")
        return False
    
    # 3. Git 상태 확인
    has_changes = check_git_status()
    
    # 4. Git 배포 실행
    if has_changes:
        if not git_add_commit_push():
            print("\n❌ Git 배포에 실패했습니다.")
            return False
    else:
        print("\nℹ️ 변경사항이 없어 Git 배포를 건너뜁니다.")
    
    # 5. 다음 단계 안내
    show_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 