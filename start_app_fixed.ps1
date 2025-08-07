# EORA AI System - PowerShell 실행 스크립트
Write-Host "====================================="
Write-Host "EORA AI System - 수정된 버전 시작"
Write-Host "====================================="

# src 디렉토리로 이동
Set-Location -Path "src"
Write-Host "현재 디렉토리: $(Get-Location)"

# Python 버전 확인
Write-Host "Python 버전 확인..."
python --version

# 필요한 패키지 설치 확인
Write-Host "필요한 패키지 설치 확인..."
pip install fastapi uvicorn python-dotenv pymongo openai pydantic

# 서버 시작
Write-Host "서버 시작 중..."
python app_fixed.py

# 대체 명령어 안내
Write-Host ""
Write-Host "만약 위 명령이 실패하면 아래 명령을 시도하세요:"
Write-Host "python -m uvicorn app_fixed:app --host 127.0.0.1 --port 8001 --reload"

pause 