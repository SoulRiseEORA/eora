# Railway 빠른 상태 확인 PowerShell 스크립트

# 실제 Railway URL로 변경하세요
$RailwayURL = "https://www.eora.life"

Write-Host "🚂 Railway 상태 확인 중..." -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

$endpoints = @(
    @{Path="/"; Name="메인 페이지"},
    @{Path="/health"; Name="헬스 체크"},
    @{Path="/docs"; Name="API 문서"}
)

foreach ($endpoint in $endpoints) {
    try {
        $url = $RailwayURL + $endpoint.Path
        $startTime = Get-Date
        
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
        $endTime = Get-Date
        $responseTime = ($endTime - $startTime).TotalMilliseconds
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($endpoint.Name): $($response.StatusCode) ($([math]::Round($responseTime, 2))ms)" -ForegroundColor Green
        } else {
            Write-Host "❌ $($endpoint.Name): $($response.StatusCode) ($([math]::Round($responseTime, 2))ms)" -ForegroundColor Red
        }
        
        # 헬스 체크 응답 내용 표시
        if ($endpoint.Path -eq "/health" -and $response.StatusCode -eq 200) {
            try {
                $data = $response.Content | ConvertFrom-Json
                Write-Host "   📊 상태: $($data.status)" -ForegroundColor Yellow
            } catch {
                # JSON 파싱 실패 시 무시
            }
        }
        
    } catch {
        Write-Host "❌ $($endpoint.Name): 연결 실패 - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "💡 팁: 실제 Railway URL로 `$RailwayURL을 변경하세요!" -ForegroundColor Yellow 