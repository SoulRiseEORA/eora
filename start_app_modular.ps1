# EORA AI System - 모듈화된 서버 시작 스크립트 (PowerShell)
Write-Host "🚀 EORA AI System - 모듈화된 서버 시작 중..."

# 환경 변수 설정
$env:OPENAI_API_KEY = "your_openai_api_key_here"
$env:DATABASE_NAME = "eora_ai"
$env:PORT = "8010"

# 현재 디렉토리 확인
$currentDir = Get-Location
Write-Host "📂 현재 디렉토리: $currentDir"

# src 디렉토리로 이동
Set-Location -Path "src"
Write-Host "📂 src 디렉토리로 이동했습니다."

# 서버 실행
Write-Host "🚀 서버를 시작합니다. (포트: $env:PORT)"
python run_railway_server.py --port $env:PORT

# 원래 디렉토리로 복귀
Set-Location -Path $currentDir 