import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Tuple
from ai_memory_wrapper import create_memory_atom_async, insert_atom_async
from aura_system.task_manager import add_task

# 로거 설정
logger = logging.getLogger(__name__)

# 이 스크립트 파일의 위치를 기준으로 절대 경로 생성
# __file__은 현재 스크립트의 경로를 나타냅니다.
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # 대화형 환경 등 __file__이 정의되지 않은 경우를 대비
    BASE_DIR = os.getcwd()

CHAT_LOGS_DIR = os.path.join(BASE_DIR, "chat_logs")

# 앱 시작 시 chat_logs 디렉토리가 없으면 생성
os.makedirs(CHAT_LOGS_DIR, exist_ok=True)

def get_session_dir(session_name: str) -> str:
    """세션 이름에 해당하는 디렉토리 경로를 반환합니다."""
    return os.path.join(CHAT_LOGS_DIR, session_name)

def get_chat_log_path(session_name: str) -> str:
    """세션의 chat.txt 파일 경로를 반환합니다."""
    return os.path.join(get_session_dir(session_name), "chat.txt")

def create_session(session_name: str) -> bool:
    """새 세션 디렉토리와 빈 chat.txt 파일을 생성합니다."""
    try:
        session_dir = get_session_dir(session_name)
        os.makedirs(session_dir, exist_ok=True)
        
        chat_path = get_chat_log_path(session_name)
        if not os.path.exists(chat_path):
            with open(chat_path, "w", encoding="utf-8") as f:
                f.write("")
        logger.info(f"세션 '{session_name}'이(가) 성공적으로 생성되었습니다.")
        return True
    except Exception as e:
        logger.error(f"세션 '{session_name}' 생성 실패: {e}", exc_info=True)
        return False

def load_session_list() -> List[str]:
    """모든 세션 목록을 불러옵니다."""
    try:
        if not os.path.isdir(CHAT_LOGS_DIR):
            logger.warning(f"채팅 로그 디렉토리를 찾을 수 없습니다: {CHAT_LOGS_DIR}")
            return []
        
        return [name for name in os.listdir(CHAT_LOGS_DIR) 
                if os.path.isdir(os.path.join(CHAT_LOGS_DIR, name))]
    except Exception as e:
        logger.error(f"세션 목록 로딩 실패: {e}", exc_info=True)
        return []

def append_message(session_name: str, role: str, content: str):
    """세션의 채팅 로그 파일에 메시지를 추가하고, 메모리 시스템에도 저장합니다."""
    try:
        session_dir = get_session_dir(session_name)
        os.makedirs(session_dir, exist_ok=True)
        chat_file_path = get_chat_log_path(session_name)
        
        # content에 포함된 개행문자를 이스케이프 처리하여 한 줄로 저장
        escaped_content = content.replace('\\', '\\\\').replace('\n', '\\n')

        with open(chat_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{role}]{escaped_content}\n")

        # 메모리 저장을 논블로킹(non-blocking) 백그라운드 태스크로 실행
        # try:
        #     add_task(save_memory_async(role, content))
        #     logger.debug(f"'{session_name}' 세션의 메시지를 메모리에 저장하도록 예약되었습니다.")
        # except Exception as e:
        #     logger.error(f"메모리 저장 작업 생성 실패: {e}", exc_info=True)
            
    except Exception as e:
        logger.error(f"'{session_name}' 세션 메시지 추가 실패: {e}", exc_info=True)

async def save_memory_async(role: str, content: str):
    """메시지를 메모리 원자로 만들어 저장하는 비동기 헬퍼 함수"""
    # 'user' 역할의 메시지만 의미 있는 기억으로 간주하여 저장 (AI 응답은 제외)
    if role.lower() == 'user':
        try:
            atom = await create_memory_atom_async(content=content, metadata={"role": role})
            await insert_atom_async(atom)
        except Exception as e:
            logger.error(f"비동기 메모리 저장 중 오류 발생: {e}", exc_info=True)

def load_messages(session_name: str) -> List[Tuple[str, str]]:
    """세션의 채팅 로그를 불러와 (역할, 내용) 튜플 리스트로 반환합니다."""
    messages = []
    try:
        chat_file_path = get_chat_log_path(session_name)
        if os.path.exists(chat_file_path):
            with open(chat_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 역할과 내용을 분리
                    if line.startswith('[') and ']' in line:
                        parts = line.split(']', 1)
                        role = parts[0][1:]
                        # 이스케이프된 개행문자를 복원
                        content = parts[1].replace('\\n', '\n').replace('\\\\', '\\')
                        messages.append((role, content))
                    else:
                        # 이전 형식과의 호환성을 위해 로그 남기기
                        logger.warning(f"'{session_name}' 세션에서 형식이 잘못된 라인을 건너뜁니다: {line}")
                        
    except Exception as e:
        logger.error(f"'{session_name}' 세션 메시지 로딩 실패: {e}", exc_info=True)
    return messages

def delete_chat_log(session_name: str):
    """세션의 채팅 로그 파일을 삭제합니다."""
    try:
        chat_file_path = get_chat_log_path(session_name)
        if os.path.exists(chat_file_path):
            os.remove(chat_file_path)
            logger.info(f"'{session_name}' 세션의 채팅 로그가 삭제되었습니다.")
    except Exception as e:
        logger.error(f"'{session_name}' 세션의 채팅 로그 삭제 실패: {e}", exc_info=True)

# 아래의 save_content, load_content는 현재 사용되지 않는 것으로 보이지만,
# 만약을 위해 경로 문제를 해결하고 유지합니다.
# 세션별로 독립적인 JSON 파일을 사용하도록 구조를 변경합니다.

def save_content(session_name: str, data: Dict[str, Any]):
    """세션 디렉토리 내에 session_data.json으로 데이터를 저장합니다."""
    try:
        session_dir = get_session_dir(session_name)
        os.makedirs(session_dir, exist_ok=True)
        path = os.path.join(session_dir, "session_data.json")
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"'{session_name}' 세션 콘텐츠 저장 오류: {e}", exc_info=True)

def load_content(session_name: str) -> Dict[str, Any]:
    """세션 디렉토리에서 session_data.json 데이터를 불러옵니다."""
    try:
        path = os.path.join(get_session_dir(session_name), "session_data.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"'{session_name}' 세션 콘텐츠 로딩 오류: {e}", exc_info=True)
        return {}

def get_session_list():
    # TODO: 실제 구현 필요. 임시로 load_session_list()를 반환
    return load_session_list()

def create_new_session(session_name):
    # TODO: 실제 구현 필요. 임시로 create_session 사용
    return create_session(session_name)

def delete_session(session_name):
    # TODO: 실제 구현 필요. 임시로 세션 디렉토리 삭제
    import shutil
    session_dir = get_session_dir(session_name)
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)
        return True
    return False
