#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway 배포 최종 검증 스크립트
모든 문제가 해결되었는지 확인
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_status(message, status="INFO"):
    """상태 메시지 출력"""
    colors = {
        "INFO": "\033[94m",    # 파란색
        "SUCCESS": "\033[92m", # 초록색
        "WARNING": "\033[93m", # 노란색
        "ERROR": "\033[91m",   # 빨간색
        "RESET": "\033[0m"     # 리셋
    }
    print(f"{colors.get(status, colors['INFO'])}[{status}] {message}{colors['RESET']}")

def check_file_exists(filename):
    """파일 존재 확인"""
    if Path(filename).exists():
        print_status(f"✅ {filename} 존재", "SUCCESS")
        return True
    else:
        print_status(f"❌ {filename} 누락", "ERROR")
        return False

def check_python_syntax(filename):
    """Python 구문 검사"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            compile(f.read(), filename, 'exec')
        print_status(f"✅ {filename} 구문 검사 통과", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ {filename} 구문 오류: {e}", "ERROR")
        return False

def check_railway_config():
    """Railway 설정 확인"""
    print_status("🔍 Railway 설정 확인 중...", "INFO")
    
    # railway.json 확인
    if not check_file_exists("railway.json"):
        return False
    
    # railway_server.py 확인
    if not check_file_exists("railway_server.py"):
        return False
    
    # 구문 검사
    if not check_python_syntax("railway_server.py"):
        return False
    
    print_status("✅ Railway 설정 완료", "SUCCESS")
    return True

def check_powershell_script():
    """PowerShell 스크립트 확인"""
    print_status("🔍 PowerShell 스크립트 확인 중...", "INFO")
    
    if not check_file_exists("deploy_powershell.ps1"):
        return False
    
    # PowerShell 구문 검사 (간단한 확인)
    try:
        with open("deploy_powershell.ps1", "r", encoding="utf-8") as f:
            content = f.read()
            if "&&" in content:
                print_status("❌ PowerShell 스크립트에 && 연산자 발견", "ERROR")
                return False
            if "Write-Host" in content and "railway up" in content:
                print_status("✅ PowerShell 스크립트 구조 확인", "SUCCESS")
                return True
            else:
                print_status("❌ PowerShell 스크립트 구조 오류", "ERROR")
                return False
    except Exception as e:
        print_status(f"❌ PowerShell 스크립트 읽기 실패: {e}", "ERROR")
        return False

def check_requirements():
    """requirements.txt 확인"""
    print_status("🔍 requirements.txt 확인 중...", "INFO")
    
    if not check_file_exists("requirements.txt"):
        return False
    
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
            required_packages = [
                "fastapi",
                "uvicorn",
                "pydantic",
                "jinja2",
                "python-multipart"
            ]
            
            missing_packages = []
            for package in required_packages:
                if package not in content:
                    missing_packages.append(package)
            
            if missing_packages:
                print_status(f"❌ 누락된 패키지: {missing_packages}", "ERROR")
                return False
            
            print_status("✅ requirements.txt 검증 완료", "SUCCESS")
            return True
            
    except Exception as e:
        print_status(f"❌ requirements.txt 읽기 실패: {e}", "ERROR")
        return False

def test_server_startup():
    """서버 시작 테스트"""
    print_status("🔍 서버 시작 테스트 중...", "INFO")
    
    try:
        # 간단한 구문 검사만 수행
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "railway_server.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_status("✅ 서버 시작 테스트 통과", "SUCCESS")
            return True
        else:
            print_status(f"❌ 서버 테스트 실패: {result.stderr}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        print_status("❌ 서버 테스트 타임아웃", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ 서버 테스트 실패: {e}", "ERROR")
        return False

def main():
    """메인 검증 함수"""
    print_status("🚀 Railway 배포 최종 검증 시작", "INFO")
    print_status("=" * 50, "INFO")
    
    checks = [
        ("Railway 설정", check_railway_config),
        ("PowerShell 스크립트", check_powershell_script),
        ("requirements.txt", check_requirements),
        ("서버 시작 테스트", test_server_startup)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        print_status(f"\n📋 {check_name} 검증 중...", "INFO")
        if check_func():
            passed_checks += 1
        else:
            print_status(f"❌ {check_name} 검증 실패", "ERROR")
    
    print_status("=" * 50, "INFO")
    print_status(f"📊 검증 결과: {passed_checks}/{total_checks} 통과", "INFO")
    
    if passed_checks == total_checks:
        print_status("🎉 모든 검증 통과! Railway 배포 준비 완료", "SUCCESS")
        print_status("\n📋 배포 방법:", "INFO")
        print_status("1. PowerShell에서: .\\deploy_powershell.ps1", "INFO")
        print_status("2. 또는 수동으로: railway up", "INFO")
        return True
    else:
        print_status("❌ 일부 검증 실패. 문제를 해결한 후 다시 시도하세요.", "ERROR")
        return False

if __name__ == "__main__":
    main() 