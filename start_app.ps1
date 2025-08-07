# EORA AI System - PowerShell 시작 스크립트
# Railway 최종 배포 버전 v2.0.0

Write-Host "🚀 EORA AI System 시작 중..." -ForegroundColor Green

# 현재 디렉토리 확인
$currentDir = Get-Location
Write-Host "📁 현재 디렉토리: $currentDir" -ForegroundColor Yellow

# src 디렉토리 확인
if (Test-Path "src") {
    Write-Host "✅ src 디렉토리 발견" -ForegroundColor Green
}
else {
    Write-Host "❌ src 디렉토리를 찾을 수 없습니다" -ForegroundColor Red
    exit 1
}

# 환경변수 확인
$openaiKey = $env:OPENAI_API_KEY
if ($openaiKey) {
    Write-Host "✅ OpenAI API 키 설정됨" -ForegroundColor Green
}
else {
    Write-Host "⚠️ OpenAI API 키가 설정되지 않았습니다" -ForegroundColor Yellow
}

# 포트 확인
$port = $env:PORT
if (-not $port) {
    $port = "8001"
}
Write-Host "🔧 서버 포트: $port" -ForegroundColor Cyan

# 서버 시작
Write-Host "🚀 FastAPI 서버 시작 중..." -ForegroundColor Green
Write-Host "📡 서버 주소: http://127.0.0.1:$port" -ForegroundColor Cyan

try {
    # uvicorn으로 서버 시작 (src.app 모듈 경로 사용)
    python -m uvicorn src.app:app --host 127.0.0.1 --port $port --reload
}
catch {
    Write-Host "❌ 서버 시작 실패: $_" -ForegroundColor Red
    
    # 대체 포트 시도
    Write-Host "🔄 대체 포트 시도 중..." -ForegroundColor Yellow
    $alternativePorts = @(8002, 8003, 8004, 8005)
    
    foreach ($altPort in $alternativePorts) {
        try {
            Write-Host "🔄 포트 $altPort 시도 중..." -ForegroundColor Yellow
            python -m uvicorn src.app:app --host 127.0.0.1 --port $altPort --reload
            break
        }
        catch {
            Write-Host "❌ 포트 $altPort 실패" -ForegroundColor Red
        }
    }
} 