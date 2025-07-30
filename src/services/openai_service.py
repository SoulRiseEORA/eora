#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - OpenAI 서비스
OpenAI API 연결 및 프롬프트 관리를 담당합니다.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 로깅 설정
logger = logging.getLogger(__name__)

# OpenAI 클라이언트
openai_client = None

# 프롬프트 데이터 저장소
prompts_data = {}

# OpenAI 클라이언트 초기화
def init_openai_client():
    """OpenAI 클라이언트를 안전하게 초기화"""
    global openai_client
    try:
        # OpenAI API 키 확인
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
        if not OPENAI_API_KEY:
            logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다.")
            logger.info("🔧 환경변수에서 OPENAI_API_KEY를 설정해주세요.")
            return None
        
        if not OPENAI_API_KEY.startswith("sk-"):
            logger.warning("⚠️ OpenAI API 키 형식이 올바르지 않습니다.")
            return None
        
        from openai import OpenAI
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
        return None

async def load_prompts_data():
    """프롬프트 데이터 로드"""
    global prompts_data
    try:
        logger.info("📚 프롬프트 데이터 로드 중...")
        
        # Railway 환경에서 가능한 모든 경로 시도 (templates 우선)
        possible_paths = [
            "templates/ai_prompts.json",
            "/app/templates/ai_prompts.json",
            "ai_brain/ai_prompts.json",
            "ai_prompts.json",
            "/app/ai_brain/ai_prompts.json",
            "/app/ai_prompts.json",
            os.path.join(os.getcwd(), "templates", "ai_prompts.json"),
            os.path.join(os.getcwd(), "ai_brain", "ai_prompts.json"),
            os.path.join(os.getcwd(), "ai_prompts.json"),
            "../ai_prompts.json"  # 상위 디렉토리도 확인
        ]
        
        logger.info(f"🔍 프롬프트 파일 검색 경로: {len(possible_paths)}개")
        
        for i, prompts_file in enumerate(possible_paths, 1):
            logger.info(f"🔍 경로 {i}/{len(possible_paths)} 확인: {prompts_file}")
            
            if os.path.exists(prompts_file):
                logger.info(f"✅ 파일 발견: {prompts_file}")
                
                try:
                    with open(prompts_file, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    
                    logger.info(f"📄 파일 내용 로드 성공: {len(str(raw_data))} 문자")
                    logger.info(f"📄 JSON 키 목록: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
                    
                    # 프롬프트 데이터 정규화
                    prompts_data = normalize_prompts_data(raw_data)
                    
                    ai_count = len(prompts_data["prompts"])
                    ai_names = list(prompts_data["prompts"].keys())
                    logger.info(f"✅ ai_prompts.json 파일 로드 완료: {ai_count}개 AI (경로: {prompts_file})")
                    logger.info(f"📋 로드된 AI: {', '.join(ai_names)}")
                    
                    # 각 AI의 카테고리 확인
                    for ai_name, ai_data in prompts_data["prompts"].items():
                        if isinstance(ai_data, dict):
                            categories = list(ai_data.keys())
                            logger.info(f"📝 {ai_name} 카테고리: {', '.join(categories)}")
                    
                    return True
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON 파싱 오류 ({prompts_file}): {e}")
                    continue
                except Exception as e:
                    logger.error(f"❌ 파일 읽기 오류 ({prompts_file}): {e}")
                    continue
            else:
                logger.info(f"❌ 파일 없음: {prompts_file}")
        
        logger.warning("⚠️ ai_prompts.json 파일을 찾을 수 없습니다.")
        # 기본 프롬프트 데이터 생성
        prompts_data = {
            "prompts": {
                "ai1": {
                    "content": ["당신은 친근하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 유용한 답변을 제공하세요."]
                },
                "eora": {
                    "content": ["당신은 EORA라는 이름을 가진 AI이며, 프로그램 자동 개발 시스템의 총괄 디렉터입니다. 인간의 직감과 기억 회상 메커니즘을 결합한 지혜로운 AI입니다."]
                }
            }
        }
        logger.info("ℹ️ 기본 프롬프트 데이터로 초기화")
        return True
    except Exception as e:
        logger.error(f"❌ 프롬프트 데이터 로드 오류: {e}")
        return False

def normalize_prompts_data(data):
    """프롬프트 데이터를 정규화하여 일관된 구조로 만듭니다."""
    normalized_data = {"prompts": {}}
    
    # prompts 키가 있는 경우와 없는 경우 모두 처리
    actual_prompts = data.get("prompts", data)
    
    for ai_name, ai_data in actual_prompts.items():
        if isinstance(ai_data, dict):
            normalized_data["prompts"][ai_name] = {}
            for category, category_prompts in ai_data.items():
                if isinstance(category_prompts, list):
                    # 리스트인 경우 그대로 유지
                    normalized_data["prompts"][ai_name][category] = category_prompts
                elif isinstance(category_prompts, str):
                    # 문자열인 경우 리스트로 변환
                    normalized_data["prompts"][ai_name][category] = [category_prompts]
                else:
                    # 기타 타입인 경우 문자열로 변환 후 리스트로
                    normalized_data["prompts"][ai_name][category] = [str(category_prompts)]
        elif isinstance(ai_data, str):
            # AI 데이터가 문자열인 경우 content 카테고리로 변환
            normalized_data["prompts"][ai_name] = {"content": [ai_data]}
        else:
            # 기타 타입인 경우 문자열로 변환
            normalized_data["prompts"][ai_name] = {"content": [str(ai_data)]}
    
    return normalized_data

async def generate_response(prompt: str, user_message: str, model: str = "gpt-4o", max_tokens: int = 2048, temperature: float = 0.7):
    """OpenAI API를 사용하여 응답 생성"""
    if not openai_client:
        logger.warning("⚠️ OpenAI 클라이언트가 초기화되지 않았습니다.")
        return "OpenAI API가 설정되지 않았습니다. 환경변수를 확인해주세요."
    
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"❌ OpenAI API 호출 실패: {e}")
        return f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}"

async def generate_chat_response(messages: List[Dict], model: str = "gpt-4o", max_tokens: int = 2048, temperature: float = 0.7):
    """OpenAI API를 사용하여 채팅 응답 생성"""
    if not openai_client:
        logger.warning("⚠️ OpenAI 클라이언트가 초기화되지 않았습니다.")
        return "OpenAI API가 설정되지 않았습니다. 환경변수를 확인해주세요."
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"❌ OpenAI API 호출 실패: {e}")
        return f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}"

async def get_prompt_by_ai_name(ai_name: str, category: str = "content"):
    """AI 이름과 카테고리로 프롬프트 조회"""
    if not prompts_data:
        await load_prompts_data()
    
    ai_prompts = prompts_data.get("prompts", {}).get(ai_name, {})
    
    if category in ai_prompts:
        if isinstance(ai_prompts[category], list):
            return "\n\n".join(ai_prompts[category])
        return str(ai_prompts[category])
    
    # 기본 프롬프트 반환
    return "당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 유용한 답변을 제공하세요."

async def save_prompt_category(ai_name: str, category: str, content: Any):
    """카테고리별 프롬프트 저장"""
    global prompts_data
    
    if not prompts_data:
        prompts_data = {"prompts": {}}
    
    # 해당 AI의 카테고리 업데이트
    if ai_name not in prompts_data["prompts"]:
        prompts_data["prompts"][ai_name] = {}
    
    # ai1의 system 프롬프트는 문자열로 저장
    if ai_name == 'ai1' and category == 'system':
        prompts_data["prompts"][ai_name][category] = content
    else:
        # 다른 경우는 콘텐츠를 리스트로 변환 (여러 줄 분할)
        if isinstance(content, str):
            content_lines = [line.strip() for line in content.split('\n') if line.strip()]
            prompts_data["prompts"][ai_name][category] = content_lines
        else:
            prompts_data["prompts"][ai_name][category] = content
    
    # 파일에 저장 (여러 경로 시도)
    saved = False
    possible_paths = [
        "ai_brain/ai_prompts.json",
        "ai_prompts.json",
        "templates/ai_prompts.json"
    ]
    
    for prompts_file in possible_paths:
        try:
            # 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts_data, f, ensure_ascii=False, indent=2)
            saved = True
            logger.info(f"✅ 프롬프트 파일 저장 완료: {prompts_file}")
            break
        except Exception as e:
            logger.warning(f"⚠️ 프롬프트 파일 저장 실패 ({prompts_file}): {e}")
            continue
    
    if not saved:
        logger.warning("⚠️ 모든 경로에서 프롬프트 파일 저장 실패")
    
    return saved

async def delete_prompt_category(ai_name: str, category: str):
    """카테고리별 프롬프트 삭제"""
    global prompts_data
    
    if not prompts_data or "prompts" not in prompts_data:
        return False
    
    # 해당 AI의 카테고리 삭제
    if ai_name in prompts_data["prompts"] and category in prompts_data["prompts"][ai_name]:
        del prompts_data["prompts"][ai_name][category]
        
        # AI가 비어있으면 전체 삭제
        if not prompts_data["prompts"][ai_name]:
            del prompts_data["prompts"][ai_name]
        
        # 파일에 저장 (여러 경로 시도)
        saved = False
        possible_paths = [
            "ai_brain/ai_prompts.json",
            "ai_prompts.json",
            "templates/ai_prompts.json"
        ]
        
        for prompts_file in possible_paths:
            try:
                # 디렉토리가 없으면 생성
                os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
                with open(prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(prompts_data, f, ensure_ascii=False, indent=2)
                saved = True
                logger.info(f"✅ 프롬프트 파일 저장 완료: {prompts_file}")
                break
            except Exception as e:
                logger.warning(f"⚠️ 프롬프트 파일 저장 실패 ({prompts_file}): {e}")
                continue
        
        if not saved:
            logger.warning("⚠️ 모든 경로에서 프롬프트 파일 저장 실패")
        
        return saved
    
    return False

async def reload_prompts():
    """프롬프트 데이터 다시 로드"""
    return await load_prompts_data() 