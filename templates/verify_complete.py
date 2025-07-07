#!/usr/bin/env python3
"""
완전 검증 스크립트 - 모든 문제 해결 확인
"""

import os
import sys
import subprocess
import time
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

def check_file_exists(file_path):
    """파일 존재 확인"""
    if Path(file_path).exists():
        print_status(f"✅ {file_path} 존재", "SUCCESS")
        return True
    else:
        print_status(f"❌ {file_path} 없음", "ERROR")
        return False

def check_python_syntax(file_path):
    """Python 구문 검사"""
    try:
        result = subprocess.run([sys.executable, "-m", "py_compile", file_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"✅ {file_path} 구문 검사 통과", "SUCCESS")
            return True
        else:
            print_status(f"❌ {file_path} 구문 오류: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ {file_path} 구문 검사 실패: {e}", "ERROR")
        return False

def check_powershell_script():
    """PowerShell 스크립트 확인"""
    print_status("🔍 PowerShell 스크립트 확인 중...", "INFO")
    
    if not check_file_exists("deploy_stable.ps1"):
        return False
    
    try:
        with open("deploy_stable.ps1", "r", encoding="utf-8") as f:
            content = f.read()
            
            # && 연산자 확인
            if "&&" in content:
                print_status("❌ PowerShell 스크립트에 && 연산자 발견", "ERROR")
                return False
            
            # 필수 요소 확인
            required_elements = [
                "Write-Host",
                "git status",
                "git add",
                "git commit",
                "railway up"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print_status(f"❌ 누락된 요소: {missing_elements}", "ERROR")
                return False
            
            print_status("✅ PowerShell 스크립트 구조 완벽", "SUCCESS")
            return True
            
    except Exception as e:
        print_status(f"❌ PowerShell 스크립트 읽기 실패: {e}", "ERROR")
        return False

def check_railway_config():
    """Railway 설정 확인"""
    print_status("🔍 Railway 설정 확인 중...", "INFO")
    
    # railway_stable.json 확인
    if not check_file_exists("railway_stable.json"):
        return False
    
    try:
        with open("railway_stable.json", "r") as f:
            config = json.load(f)
            
            # 필수 키 확인
            required_keys = ["build", "deploy"]
            for key in required_keys:
                if key not in config:
                    print_status(f"❌ Railway 설정에 {key} 누락", "ERROR")
                    return False
            
            # 시작 명령어 확인
            start_cmd = config.get("deploy", {}).get("startCommand")
            if start_cmd != "python stable_server.py":
                print_status(f"❌ Railway 시작 명령어 오류: {start_cmd}", "ERROR")
                return False
            
            print_status("✅ Railway 설정 완벽", "SUCCESS")
            return True
            
    except Exception as e:
        print_status(f"❌ Railway 설정 읽기 실패: {e}", "ERROR")
        return False

def test_server_startup():
    """서버 시작 테스트"""
    print_status("🔍 서버 시작 테스트 중...", "INFO")
    
    if not check_file_exists("stable_server.py"):
        return False
    
    if not check_python_syntax("stable_server.py"):
        return False
    
    try:
        # 서버 시작 테스트 (3초 후 종료)
        process = subprocess.Popen([
            sys.executable, "stable_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)  # 3초 대기
        
        # 프로세스가 살아있는지 확인
        if process.poll() is None:
            print_status("✅ 서버 시작 성공", "SUCCESS")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print_status(f"❌ 서버 시작 실패: {stderr.decode()}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ 서버 테스트 실패: {e}", "ERROR")
        return False

def check_requirements():
    """requirements.txt 확인"""
    print_status("🔍 requirements.txt 확인 중...", "INFO")
    
    if not check_file_exists("requirements.txt"):
        return False
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
            required_packages = [
                "fastapi",
                "uvicorn",
                "jinja2",
                "pydantic"
            ]
            
            missing_packages = []
            for package in required_packages:
                if package not in content:
                    missing_packages.append(package)
            
            if missing_packages:
                print_status(f"❌ 누락된 패키지: {missing_packages}", "ERROR")
                return False
            else:
                print_status("✅ 필수 패키지 모두 포함", "SUCCESS")
                return True
    except Exception as e:
        print_status(f"❌ requirements.txt 읽기 실패: {e}", "ERROR")
        return False

def check_templates():
    """템플릿 파일 확인"""
    print_status("🔍 템플릿 파일 확인 중...", "INFO")
    
    templates_dir = Path("templates")
    if not templates_dir.exists():
        print_status("❌ templates 디렉토리가 없습니다", "ERROR")
        return False
    
    required_templates = ["home.html", "chat.html"]
    missing_templates = []
    
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print_status(f"✅ {template} 존재", "SUCCESS")
        else:
            print_status(f"❌ {template} 없음", "ERROR")
            missing_templates.append(template)
    
    if missing_templates:
        return False
    
    print_status("✅ 모든 템플릿 파일 존재", "SUCCESS")
    return True

def main():
    """메인 검증 함수"""
    print_status("🚀 완전 검증 시작", "INFO")
    print_status("=" * 50, "INFO")
    
    checks = [
        ("Railway 설정", check_railway_config),
        ("PowerShell 스크립트", check_powershell_script),
        ("requirements.txt", check_requirements),
        ("템플릿 파일", check_templates),
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
        print_status("🎉 모든 검증 통과! 완전 안정 배포 준비 완료", "SUCCESS")
        print_status("\n📋 배포 방법:", "INFO")
        print_status("1. PowerShell에서: .\\deploy_stable.ps1", "INFO")
        print_status("2. 또는 수동으로: railway up", "INFO")
        print_status("\n🎯 모든 문제가 해결되었습니다!", "SUCCESS")
        return True
    else:
        print_status("❌ 일부 검증 실패. 문제를 해결한 후 다시 시도하세요.", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 