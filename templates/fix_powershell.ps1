# PowerShell 환경 문제 해결 스크립트
Write-Host "========================================" -ForegroundColor Green
Write-Host "EORA AI System PowerShell 환경 수정" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 1. 실행 정책 확인 및 수정
Write-Host "`n1. PowerShell 실행 정책 확인..." -ForegroundColor Yellow
$policy = Get-ExecutionPolicy
Write-Host "현재 실행 정책: $policy" -ForegroundColor Cyan

if ($policy -eq "Restricted") {
    Write-Host "실행 정책을 RemoteSigned로 변경합니다..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "실행 정책 변경 완료" -ForegroundColor Green
}

# 2. 포트 사용 중인 프로세스 확인 및 종료
Write-Host "`n2. 포트 8005 사용 중인 프로세스 확인..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8005 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($processes) {
    Write-Host "포트 8005를 사용 중인 프로세스 발견:" -ForegroundColor Red
    foreach ($processId in $processes) {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  - PID: $processId, 이름: $($process.ProcessName)" -ForegroundColor Red
            Write-Host "    프로세스를 종료합니다..." -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    }
} else {
    Write-Host "포트 8005를 사용 중인 프로세스가 없습니다." -ForegroundColor Green
}

# 3. Python 프로세스 확인
Write-Host "`n3. Python 프로세스 확인..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "실행 중인 Python 프로세스:" -ForegroundColor Cyan
    $pythonProcesses | ForEach-Object {
        Write-Host "  - PID: $($_.Id), 이름: $($_.ProcessName)" -ForegroundColor Cyan
    }
} else {
    Write-Host "실행 중인 Python 프로세스가 없습니다." -ForegroundColor Green
}

# 4. Git 상태 확인
Write-Host "`n4. Git 저장소 상태 확인..." -ForegroundColor Yellow
$gitPath = "E:\AI_Dev_Tool\src"
if (Test-Path "$gitPath\.git") {
    Write-Host "Git 저장소 발견: $gitPath" -ForegroundColor Green
    Set-Location $gitPath
    Write-Host "Git 상태:" -ForegroundColor Cyan
    git status
} else {
    Write-Host "Git 저장소를 찾을 수 없습니다: $gitPath" -ForegroundColor Red
}

# 5. 서버 시작 준비
Write-Host "`n5. 서버 시작 준비..." -ForegroundColor Yellow
Write-Host "다음 명령으로 서버를 시작할 수 있습니다:" -ForegroundColor Cyan
Write-Host "  python main.py --port 8005" -ForegroundColor White
Write-Host "  또는" -ForegroundColor White
Write-Host "  python main.py --port 8006" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "PowerShell 환경 수정 완료" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Read-Host "`n계속하려면 Enter를 누르세요" 