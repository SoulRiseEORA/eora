# EORA AI System 서버 시작 스크립트
Write-Host "🚀 EORA AI System 서버 시작 중..." -ForegroundColor Green
Write-Host ""

# 현재 디렉토리로 이동
Set-Location $PSScriptRoot

# 포트 사용 상태 확인
$port8081 = Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue
if ($port8081) {
    Write-Host "⚠️ 포트 8081이 이미 사용 중입니다." -ForegroundColor Yellow
    Write-Host "🔍 다른 포트로 시도합니다..." -ForegroundColor Yellow
    $port = 8082
}
else {
    $port = 8081
}

Write-Host "📍 사용 포트: $port" -ForegroundColor Cyan
Write-Host ""

# 서버 시작
try {
    python -m uvicorn main:app --host 127.0.0.1 --port $port --reload
}
catch {
    Write-Host "❌ 서버 시작 실패: $_" -ForegroundColor Red
    Read-Host "계속하려면 아무 키나 누르세요"
} 