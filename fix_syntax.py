#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_syntax_errors():
    print("🔧 app.py 문법 오류 수정 중...")
    
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. MongoDB URL 처리 들여쓰기 수정
    content = content.replace(
        """    for url in local_urls:
            if url and url not in urls_to_try:
            urls_to_try.append(url)""",
        """    for url in local_urls:
        if url and url not in urls_to_try:
            urls_to_try.append(url)"""
    )
    
    # 2. OpenAI 클라이언트 초기화 수정
    content = content.replace(
        """    from openai import OpenAI
        # Railway 호환 OpenAI 클라이언트 초기화
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0,  # Railway 환경에서 타임아웃 설정
            max_retries=3   # 재시도 횟수 설정
        )
        
        logger.info("✅ OpenAI API 클라이언트 초기화 성공")
        return openai_client
        
except ImportError as e:
        logger.error(f"❌ OpenAI 모듈 import 실패: {e}")
        logger.info("💡 requirements.txt에 openai>=1.3.0이 포함되어 있는지 확인해주세요.")
        return None
except Exception as e:
        logger.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        logger.warning("⚠️ OpenAI 기능이 비활성화됩니다. 환경변수를 확인해주세요.")
        return None""",
        """        from openai import OpenAI
        # Railway 호환 OpenAI 클라이언트 초기화
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0,  # Railway 환경에서 타임아웃 설정
            max_retries=3   # 재시도 횟수 설정
        )
        
        logger.info("✅ OpenAI API 클라이언트 초기화 성공")
        return openai_client
        
    except ImportError as e:
        logger.error(f"❌ OpenAI 모듈 import 실패: {e}")
        logger.info("💡 requirements.txt에 openai>=1.3.0이 포함되어 있는지 확인해주세요.")
        return None
    except Exception as e:
        logger.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        logger.warning("⚠️ OpenAI 기능이 비활성화됩니다. 환경변수를 확인해주세요.")
        return None"""
    )
    
    # 3. try 블록 외부의 잘못된 except 문들 수정
    content = content.replace(
        """# OpenAI 클라이언트 초기화 실행
try:
    openai_client = init_openai_client()
    if openai_client:
        logger.info("✅ OpenAI API 키 설정 성공 (Railway 호환)")""",
        """# OpenAI 클라이언트 초기화 실행
try:
    openai_client = init_openai_client()
    if openai_client:
        logger.info("✅ OpenAI API 키 설정 성공 (Railway 호환)")
    else:
        logger.warning("⚠️ OpenAI 클라이언트 초기화 실패")
except Exception as e:
    logger.error(f"❌ OpenAI 클라이언트 초기화 중 오류: {e}")
    openai_client = None"""
    )
    
    # 파일 저장
    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ 문법 오류 수정 완료!")

if __name__ == "__main__":
    fix_syntax_errors() 