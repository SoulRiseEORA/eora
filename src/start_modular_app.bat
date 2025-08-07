@echo off
echo ======================================
echo EORA AI 시스템 모듈화 버전 실행
echo ======================================

cd %~dp0
echo 작업 디렉토리: %cd%

echo 모듈화된 서버 시작 중...
python run_modular_server.py

pause 