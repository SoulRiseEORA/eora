#!/usr/bin/env python3
"""
🚀 Railway 완벽 시작 스크립트
모든 환경변수와 경로 문제를 완벽하게 처리
"""
import os
import sys
import uvicorn
from pathlib import Path

def get_port():
    """Railway PORT 환경변수를 안전하게 가져오기"""
    try:
        port = os.environ.get('PORT', '8080')
        return int(port)
    except (ValueError, TypeError):
        print(f"⚠️ PORT 환경변수 오류: {os.environ.get('PORT')} → 기본값 8080 사용")
        return 8080

def setup_python_path():
    """Python 경로 완벽 설정"""
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    
    # src 디렉토리를 최우선으로 추가
    if src_dir.exists():
        src_path = str(src_dir.absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        print(f"✅ Python 경로 추가: {src_path}")
    
    return src_dir

def main():
    """Railway 완벽 시작"""
    print("🚀 Railway 완벽 시작 스크립트")
    print(f"📁 현재 디렉토리: {Path.cwd()}")
    print(f"🐍 Python 버전: {sys.version}")
    
    # 포트 설정
    port = get_port()
    host = "0.0.0.0"
    print(f"🔌 서버 포트: {port}")
    print(f"📍 서버 호스트: {host}")
    
    # Python 경로 설정
    src_dir = setup_python_path()
    
    # 환경변수 출력 (디버깅용)
    print(f"🔑 PORT 환경변수: {os.environ.get('PORT', 'None')}")
    print(f"📂 sys.path: {sys.path[:3]}...")  # 처음 3개만 출력
    
    try:
        # FastAPI 앱 import 시도
        print("🔄 FastAPI 앱 로드 시도...")
        
        # 방법 1: src 디렉토리에서 직접 import
        try:
            from app import app
            print("✅ FastAPI 앱 로드 성공 (직접 import)")
        except ImportError as e1:
            print(f"⚠️ 직접 import 실패: {e1}")
            
            # 방법 2: src 모듈로 import
            try:
                from src.app import app
                print("✅ FastAPI 앱 로드 성공 (src 모듈)")
            except ImportError as e2:
                print(f"⚠️ src 모듈 import 실패: {e2}")
                
                # 방법 3: 절대 경로로 import
                try:
                    import importlib.util
                    app_path = src_dir / "app.py"
                    if app_path.exists():
                        spec = importlib.util.spec_from_file_location("app", app_path)
                        app_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(app_module)
                        app = app_module.app
                        print("✅ FastAPI 앱 로드 성공 (절대 경로)")
                    else:
                        raise ImportError(f"app.py 파일을 찾을 수 없음: {app_path}")
                except Exception as e3:
                    print(f"❌ 모든 import 방법 실패:")
                    print(f"   1. 직접 import: {e1}")
                    print(f"   2. src 모듈: {e2}")
                    print(f"   3. 절대 경로: {e3}")
                    print(f"📂 확인된 파일들: {list(src_dir.glob('*.py')) if src_dir.exists() else 'src 디렉토리 없음'}")
                    sys.exit(1)
        
        print("🌐 uvicorn 서버 시작...")
        
        # uvicorn 실행 - 모든 설정 완벽 적용
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            use_colors=False,  # Railway 로그 호환
            server_header=False,
            date_header=False,
            reload=False,  # Railway에서는 reload 비활성화
            workers=1
        )
        
    except KeyboardInterrupt:
        print("🛑 서버 중단됨 (Ctrl+C)")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        print(f"❌ 오류 타입: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()