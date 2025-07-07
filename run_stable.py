#!/usr/bin/env python3
"""
EORA AI 서버 안정 실행 스크립트 (모든 오류 처리 포함)
"""

import uvicorn
import os
import sys
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Railway 환경변수에서 포트 가져오기 (기본값을 8005로 변경)
    port = int(os.environ.get("PORT", 8005))
    
    print(f"🚀 EORA AI 서버를 안정적으로 시작합니다...")
    print(f"📍 주소: http://127.0.0.1:{port}")
    print(f"📋 사용 가능한 페이지:")
    print(f"   - 홈: http://127.0.0.1:{port}/")
    print(f"   - 디버그: http://127.0.0.1:{port}/debug")
    print(f"   - 채팅: http://127.0.0.1:{port}/chat")
    print(f"   - 상태 확인: http://127.0.0.1:{port}/health")
    print(f"   - API 테스트: http://127.0.0.1:{port}/api_test.html")
    print("=" * 50)
    
    try:
        # 안정적인 서버 실행 (reload=False, 모든 오류 처리)
        uvicorn.run(
            "main:app", 
            host="127.0.0.1", 
            port=port, 
            reload=False,  # 파일 변경 감지 비활성화
            log_level="info",
            access_log=True,
            use_colors=True
        )
    except KeyboardInterrupt:
        print("\n🛑 서버가 사용자에 의해 중지되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류 발생: {str(e)}")
        logger.error(f"서버 실행 실패: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 