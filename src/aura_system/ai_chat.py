"""
 AI 채팅 시스템
- 대화 처리
- 응답 생성
- 메모리 관리
- 분석 통합
"""
import os
import sys
import json
import logging
import asyncio
import re
import datetime
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI
from aura_system.memory_manager import get_memory_manager
from aura_system.analysis import Analysis
from aura_system.truth_sense import TruthSense
from aura_system.self_realizer import SelfRealizer
from aura_system.recall_engine import RecallEngine
from aura_system.insight_engine import InsightEngine
from aura_system.config import get_config
sys.path.append(os.path.join(os.path.dirname(__file__), '../EORA/eora_modular'))
from evaluate_eora_turn import evaluate_eora_turn
from EORA.prompt_storage_modifier import handle_prompt_save_command
from aura_system.file_loader import load_file_and_store_memory, split_text_into_chunks
import glob
import time
import uuid
from EORA.eora_modular.memory_chain_v4 import MemoryNode, MemoryChain
from EORA.eora_modular.recall_engine_v3 import RecallEngineV3 as ModularRecallEngine
from EORA_GAI.eai_launcher import initialize_eai

# 외부 라이브러리 디버그/INFO 로그 차단
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING, force=True)

logger = logging.getLogger(__name__)

# --- 싱글톤 관리를 위한 전역 변수 ---
_eora_ai_instance = None
_eai_system_instance = None

memory_chain_manager = MemoryChain()
modular_recall_engine = ModularRecallEngine()

def load_triggers(filename: str, default_values: Dict) -> Dict:
    """JSON 설정 파일을 안전하게 로드하는 범용 함수"""
    try:
        filepath = os.path.join(os.path.dirname(__file__), "prompts", filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ {filename} 파일 로드 실패: {e}", exc_info=True)
        return default_values


def load_ai1_system_prompt():
    """ai_prompts.json에서 시스템 프롬프트를 로드합니다."""
    try:
        filepath = "ai_brain/ai_prompts.json"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        ai1 = data.get("ai1", {})
        system_prompt = ai1.get("system", [])
        # 이중 리스트(문자열로 감싼 리스트) 복구
        if isinstance(system_prompt, list):
            flat = []
            for item in system_prompt:
                if isinstance(item, str) and item.strip().startswith("[") and item.strip().endswith("]"):
                    try:
                        import ast
                        parsed = ast.literal_eval(item)
                        if isinstance(parsed, list):
                            flat.extend(parsed)
                        else:
                            flat.append(item)
                    except Exception:
                        flat.append(item)
                else:
                    flat.append(item)
            system_prompt = flat
        elif isinstance(system_prompt, str):
            # 혹시 문자열 전체가 리스트라면 파싱
            try:
                import ast
                parsed = ast.literal_eval(system_prompt)
                if isinstance(parsed, list):
                    system_prompt = parsed
                else:
                    system_prompt = [system_prompt]
            except Exception:
                system_prompt = [system_prompt]
        # 공백/빈 항목/중복 제거
        system_prompt = [s.strip() for s in system_prompt if s and s.strip()]
        system_prompt = list(dict.fromkeys(system_prompt))
        return "\n".join(system_prompt)
    except Exception as e:
        logger.error(f"❌ 시스템 프롬프트 로드 실패: {e}", exc_info=True)
        return "당신은 EORA AI입니다. (프롬프트 로딩 실패)"


def save_ai1_system_prompt(new_prompt_text: str) -> bool:
    """ai1의 시스템 프롬프트를 ai_prompts.json 파일에 추가합니다."""
    try:
        filepath = "ai_brain/ai_prompts.json"
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"ai1": {"system": []}}

        if "ai1" not in data:
            data["ai1"] = {}
        existing_prompt_data = data["ai1"].get("system", [])
        # 이중 리스트(문자열로 감싼 리스트) 복구
        flat = []
        if isinstance(existing_prompt_data, list):
            for item in existing_prompt_data:
                if isinstance(item, str) and item.strip().startswith("[") and item.strip().endswith("]"):
                    try:
                        import ast
                        parsed = ast.literal_eval(item)
                        if isinstance(parsed, list):
                            flat.extend(parsed)
                        else:
                            flat.append(item)
                    except Exception:
                        flat.append(item)
                else:
                    flat.append(item)
        elif isinstance(existing_prompt_data, str):
            try:
                import ast
                parsed = ast.literal_eval(existing_prompt_data)
                if isinstance(parsed, list):
                    flat = parsed
                else:
                    flat = [existing_prompt_data]
            except Exception:
                flat = [existing_prompt_data]
        else:
            flat = list(existing_prompt_data)
        # new_prompt_text가 dict/JSON 등 다양한 형식일 때 문자열만 추출
        import json as _json
        import ast
        prompt_candidates = []
        # 1. dict 타입이면 'prompt' 키만 추출
        if isinstance(new_prompt_text, dict):
            if 'prompt' in new_prompt_text and isinstance(new_prompt_text['prompt'], str):
                prompt_candidates.append(new_prompt_text['prompt'])
            else:
                # dict 내 모든 값 중 문자열만 추출
                for v in new_prompt_text.values():
                    if isinstance(v, str):
                        prompt_candidates.append(v)
        # 2. JSON 문자열이면 파싱해서 'prompt' 키만 추출
        else:
            try:
                parsed = _json.loads(new_prompt_text)
                if isinstance(parsed, dict):
                    if 'prompt' in parsed and isinstance(parsed['prompt'], str):
                        prompt_candidates.append(parsed['prompt'])
                    else:
                        # dict 내 모든 값 중 문자열만 추출
                        for v in parsed.values():
                            if isinstance(v, str):
                                prompt_candidates.append(v)
                elif isinstance(parsed, list):
                    for v in parsed:
                        if isinstance(v, str):
                            prompt_candidates.append(v)
            except Exception:
                # 3. 일반 문자열이면 그대로 사용
                if isinstance(new_prompt_text, str):
                    prompt_candidates.extend([s.strip() for s in new_prompt_text.split("\n") if s and s.strip()])
        # 모든 후보를 문자열로 강제 변환 (혹시라도 남아있을 수 있는 비문자열 방지)
        prompt_candidates = [str(s).strip() for s in prompt_candidates if s and str(s).strip()]
        # 기존 + 신규 합치고 중복/빈 항목/공백 제거
        updated_prompt = flat + prompt_candidates
        updated_prompt = [s for s in updated_prompt if s and s.strip()]
        updated_prompt = list(dict.fromkeys(updated_prompt))
        data["ai1"]["system"] = updated_prompt
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # logger.info(f"✅ 시스템 프롬프트가 {filepath}에 성공적으로 업데이트되었습니다.")
        return True
    except Exception as e:
        logger.error(f"❌ 시스템 프롬프트 저장 실패: {e}", exc_info=True)
        return False


def get_eai_system():
    global _eai_system_instance
    if _eai_system_instance is None:
        _eai_system_instance = initialize_eai()
    return _eai_system_instance


class EORAAI:
    """EORA AI 시스템"""
    
    def _get_valid_api_key(self):
        """통합 API 키 검색 로직"""
        import os
        
        # 여러 가능한 환경변수 이름 시도
        possible_keys = [
            "OPENAI_API_KEY",
            "OPENAI_API_KEY_1", 
            "OPENAI_API_KEY_2",
            "OPENAI_API_KEY_3",
            "OPENAI_API_KEY_4",
            "OPENAI_API_KEY_5"
        ]
        
        # 환경 변수에서 찾기
        for key_name in possible_keys:
            key_value = os.getenv(key_name)
            if key_value and key_value.startswith("sk-") and len(key_value) > 50:
                logger.info(f"✅ AURA AI - 유효한 API 키 발견: {key_name}")
                # 환경변수에 강제로 설정하여 일관성 보장
                os.environ["OPENAI_API_KEY"] = key_value
                return key_value
        
        logger.warning("⚠️ AURA AI - 유효한 OpenAI API 키를 찾을 수 없습니다")
        return None

    def __init__(self, memory_manager):
        if memory_manager is None:
            raise RuntimeError("EORAAI는 반드시 memory_manager와 함께 초기화되어야 합니다.")
        
        # 통합 API 키 검색 사용
        api_key = self._get_valid_api_key()
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("✅ AURA AI OpenAI 클라이언트 초기화 완료 (통합 키 검색)")
        else:
            logger.error("❌ 유효한 OpenAI API 키를 찾을 수 없습니다")
            self.client = None
        
        self.memory_manager = memory_manager
        self.eai_system = get_eai_system()  # EAI 시스템 인스턴스 보유
        if not self.eai_system:
            logger.error("❌ EAI 시스템 인스턴스 생성 실패!")
        else:
            logger.info("✅ EAI 시스템 인스턴스 정상 생성됨.")
        self.analysis = Analysis()
        self.recall_engine = RecallEngine(memory_manager)
        self.insight_engine = InsightEngine()
        self.truth_sense = TruthSense()
        self.self_realizer = SelfRealizer()
        self.turn_count = 0
        self.last_analysis_results = {}
        self.last_user_input = ""
        self.last_gpt_response = ""
        self.dialogue_history_for_insight = []
        self.last_attached_file_path = None  # 첨부파일 경로 상태 저장
        
    async def initialize(self):
        await self.analysis.initialize()
        # logger.info("✅ EORA AI 초기화 완료")
            
    async def respond_async(self, user_input: str, trigger_context: dict = None, eai_system: Any = None, recall_context: list = None) -> Dict[str, Any]:
        """사용자 입력에 응답하고 전체 워크플로우를 관리합니다."""
        # user_input이 list 타입일 경우 무조건 문자열로 변환 (모든 분기 전에 반드시 실행)
        if not isinstance(user_input, str):
            if isinstance(user_input, (list, tuple, set)):
                user_input = " ".join([str(u) for u in user_input])
            else:
                user_input = str(user_input)
        
        # 날짜/요일 파싱 유틸리티
        import re
        import datetime
        import calendar
        def parse_date_info(text):
            # '17일', '2024-06-17', '다음주 수요일', '수요일', '월요일', '내일', '모레' 등
            today = datetime.date.today()
            weekdays_kr = ['월요일','화요일','수요일','목요일','금요일','토요일','일요일']
            weekdays_en = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
            info = {}
            # YYYY-MM-DD
            m = re.search(r'(20\d{2})[\-/.](\d{1,2})[\-/.](\d{1,2})', text)
            if m:
                y, mth, d = map(int, m.groups())
                try:
                    dt = datetime.date(y, mth, d)
                    info['date'] = dt.isoformat()
                except:
                    pass
            # 17일, 6월 17일
            m = re.search(r'(\d{1,2})월\s*(\d{1,2})일', text)
            if m:
                mth, d = map(int, m.groups())
                y = today.year
                try:
                    dt = datetime.date(y, mth, d)
                    info['date'] = dt.isoformat()
                except:
                    pass
            else:
                m = re.search(r'(\d{1,2})일', text)
                if m:
                    d = int(m.group(1))
                    y = today.year
                    mth = today.month
                    try:
                        dt = datetime.date(y, mth, d)
                        info['date'] = dt.isoformat()
                    except:
                        pass
            # 요일
            for i, w in enumerate(weekdays_kr):
                if w in text:
                    info['weekday'] = w
            for i, w in enumerate(weekdays_en):
                if w in text.lower():
                    info['weekday'] = weekdays_kr[i]
            # 상대적 날짜: 내일, 모레, 다음주 수요일 등
            if '내일' in text:
                dt = today + datetime.timedelta(days=1)
                info['date'] = dt.isoformat()
                info['weekday'] = weekdays_kr[dt.weekday()]
            if '모레' in text:
                dt = today + datetime.timedelta(days=2)
                info['date'] = dt.isoformat()
                info['weekday'] = weekdays_kr[dt.weekday()]
            if '다음주' in text:
                # 다음주 + 요일
                for i, w in enumerate(weekdays_kr):
                    if w in text:
                        # 이번주 해당 요일까지 남은 일수
                        days_ahead = (i - today.weekday() + 7) % 7
                        if days_ahead == 0:
                            days_ahead = 7
                        dt = today + datetime.timedelta(days=days_ahead+7)
                        info['date'] = dt.isoformat()
                        info['weekday'] = w
            return info

        # === 첨부파일 안내 메시지 처리 ===
        if user_input.startswith("첨부파일:"):
            # 예: '첨부파일: example.txt' 형식
            file_path = user_input.replace("첨부파일:", "").strip()
            self.last_attached_file_path = file_path
            return {
                "role": "EORA",
                "response": f"✅ 파일({os.path.basename(file_path)})이(가) 첨부되었습니다.",
                "tasks": [],
                "analysis": {},
                "eai_analysis": {},
                "memories": [],
                "truth": None,
                "self_realization": None,
            }
        # === 첨부파일/학습/기억 명령 처리 ===
        file_cmd_patterns = [
            r"파일(을)? 첨부", r"첨부파일", r"파일 업로드", r"파일 분석", r"파일 학습", r"파일 기억", r"파일 저장",
            r"학습해", r"기억해", r"저장해", r"분석하여 저장하라", r"대용량 텍스트 학습", r"대용량 텍스트 기억"
        ]
        if any(re.search(p, user_input) for p in file_cmd_patterns):
            responses = []
            print(f"[DEBUG] last_attached_file_path: {self.last_attached_file_path}")
            print(f"[DEBUG] user_input: {user_input} (type: {type(user_input)})")
            # 1. 첨부파일 우선 처리
            file_path = None
            if self.last_attached_file_path and os.path.exists(self.last_attached_file_path):
                file_path = self.last_attached_file_path
            else:
                m = re.search(r"([\w\./\\-]+\.(txt|md|csv|log|json|pdf|docx))", user_input)
                if m:
                    file_path = m.group(1)
                if not file_path:
                    files = glob.glob("./uploads/*.*") + glob.glob("./docs/*.*")
                    if files:
                        file_path = files[-1]
            print(f"[DEBUG] file_path: {file_path}")
            if file_path and os.path.exists(file_path):
                responses.append(f"파일을 청크로 분할 및 메모리에 저장 중...")
                try:
                    await load_file_and_store_memory(file_path)
                except Exception as e:
                    print(f"[ERROR] load_file_and_store_memory 예외: {e}")
                    responses.append(f"파일 학습 중 오류 발생: {e}")
                    return {
                        "role": "EORA",
                        "response": responses,
                        "tasks": [],
                        "analysis": {},
                        "eai_analysis": {},
                        "memories": [],
                        "truth": None,
                        "self_realization": None,
                    }
                responses.append("메모리에 저장 완료!")
                self.last_attached_file_path = None
                return {
                    "role": "EORA",
                    "response": responses,  # 프론트에서 순차 출력
                    "tasks": [],
                    "analysis": {},
                    "eai_analysis": {},
                    "memories": [],
                    "truth": None,
                    "self_realization": None,
                }
            else:
                # 텍스트 입력(붙여넣기)도 청크 분할 저장
                text = user_input
                chunks = split_text_into_chunks(text)
                responses.append(f"입력하신 내용을 청크로 분할 중...")
                responses.append(f"총 {len(chunks)}개의 청크로 분할 완료.")
                for idx, chunk in enumerate(chunks):
                    chunk_date_info = parse_date_info(chunk)
                    try:
                        print(f"[DEBUG] 텍스트 청크 저장: idx={idx}, chunk={chunk[:50]}...")
                        await self.memory_manager.store_memory(
                            content=chunk,
                            metadata={"type": "file_chunk", "chunk_index": idx, "source": file_path, "timestamp": datetime.datetime.utcnow().isoformat(), **chunk_date_info}
                        )
                    except Exception as e:
                        print(f"[ERROR] 텍스트 청크 저장 예외: idx={idx}, error={e}")
                responses.append("메모리에 저장 완료!")
                return {
                    "role": "EORA",
                    "response": responses,
                    "tasks": [],
                    "analysis": {},
                    "eai_analysis": {},
                    "memories": [],
                    "truth": None,
                    "self_realization": None,
                }
        # === 분석 요약 명령 처리 ===
        if "분석 요약" in user_input:
            # 최근 첨부파일 또는 최근 저장된 파일 내용 요약
            file_path = self.last_attached_file_path
            if not file_path:
                files = glob.glob("./uploads/*.*") + glob.glob("./docs/*.*")
                if files:
                    file_path = files[-1]
            if file_path and os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                # 간단 요약(여기서는 앞 500자만, 실제로는 요약 엔진 활용 가능)
                summary = text[:500] + ("..." if len(text) > 500 else "")
                return {
                    "role": "EORA",
                    "response": f"{os.path.basename(file_path)} 파일의 요약: {summary}",
                    "tasks": [],
                    "analysis": {},
                    "eai_analysis": {},
                    "memories": [],
                    "truth": None,
                    "self_realization": None,
                }
            else:
                return {
                    "role": "EORA",
                    "response": "요약할 첨부파일이 없습니다.",
                    "tasks": [],
                    "analysis": {},
                    "eai_analysis": {},
                    "memories": [],
                    "truth": None,
                    "self_realization": None,
                }
        # === 프롬프트 저장 명령 처리 ===
        if "프롬프트로 저장" in user_input:
            ok, msg = handle_prompt_save_command(user_input)
            # logger.info(f"[프롬프트 저장 명령] {msg}")
            # 안내 메시지로 바로 반환 (실제 assistant 응답)
            return {
                "role": "EORA",
                "response": msg,
                "tasks": [],
                "analysis": {},
                "eai_analysis": {},
                "memories": [],
                "truth": None,
                "self_realization": None,
            }

        # EAI 처리
        eai_analysis_result = {}
        if eai_system is None:
            eai_system = self.eai_system
        if eai_system:
            # logger.info("⚡️ EAI 시스템이 응답 처리를 시작합니다.")
            try:
                eai_analysis_result = await eai_system.process_response(user_input, {})
                # logger.info(f"✅ EAI 처리 완료: {eai_analysis_result}")
            except Exception as e:
                logger.error(f"❌ EAI 처리 중 오류 발생: {e}", exc_info=True)
        else:
            logger.warning("⚠️ EAI 시스템이 제공되지 않아, 일반 응답 로직을 실행합니다.")

        # 턴 수 증가
        self.turn_count += 1
        config = get_config()
        recall_threshold = config.get('memory.recall_threshold', 0.7)
        # 기존 분석/회상/통찰 분기 및 결과 변수 유지
        analysis_task = None
        recall_task = None
        insight_task = None
        analysis_result = self.last_analysis_results if hasattr(self, 'last_analysis_results') else {}
        insight_text = ""
        tone_analysis_result = None
        try:
            if self.turn_count % 5 == 1:
                analysis_task = self.analysis.analyze(user_input, context={})
            # === 여러 회상 전략 병렬 실행 및 통합 ===
            recall_tasks = []
            # 1. 임베딩/직감 기반
            embedding_recall_task = self.recall_engine.recall(user_input, distance_threshold=recall_threshold, limit=10)
            recall_tasks.append(embedding_recall_task)
            # 2. 신념/키워드 기반
            belief_recall_task = None
            if hasattr(self.recall_engine, 'recall_by_belief'):
                belief_recall_task = asyncio.to_thread(self.recall_engine.recall_by_belief, user_input)
                recall_tasks.append(belief_recall_task)
            # 3. 감정 기반
            emotion_recall_task = None
            if hasattr(self.recall_engine, 'recall_by_emotion_analysis'):
                emotion_recall_task = asyncio.to_thread(self.recall_engine.recall_by_emotion_analysis, user_input)
                recall_tasks.append(emotion_recall_task)
            # 4. 메타데이터 기반(날짜 등)
            query_date_info = parse_date_info(user_input)
            metadata_recall_task = None
            if query_date_info and hasattr(self.memory_manager, 'search_by_metadata'):
                metadata_recall_task = self.memory_manager.search_by_metadata(query_date_info)
                recall_tasks.append(metadata_recall_task)
            # 5. file_chunk 타입 recall(첨부파일 청크 회상)도 항상 병렬로 추가
            file_chunk_recall = []
            if hasattr(self.memory_manager, 'search_by_metadata'):
                file_chunk_recall = await self.memory_manager.search_by_metadata({"type": "file_chunk"}, top_k=20)
            # 병렬 실행 with 타임아웃 (recall_tasks가 비어있으면 빈 리스트)
            try:
                recall_results = await asyncio.wait_for(
                    asyncio.gather(*recall_tasks, return_exceptions=True), 
                    timeout=3  # 전체 회상 과정에 3초 타임아웃
                ) if recall_tasks else []
                # 예외가 발생한 결과는 빈 리스트로 처리
                recall_results = [result if not isinstance(result, Exception) else [] for result in recall_results]
            except asyncio.TimeoutError:
                logger.warning("⚡️ 메모리 회상 타임아웃 (3초) - 빠른 응답을 위해 건너뜀")
                recall_results = [[] for _ in recall_tasks] if recall_tasks else []
            # 전략별로 분리
            embedding_recall = recall_results[0] if len(recall_results) > 0 else []
            belief_recall = recall_results[1] if belief_recall_task and len(recall_results) > 1 else []
            emotion_recall = recall_results[2] if emotion_recall_task and len(recall_results) > 2 else []
            metadata_recall = recall_results[3] if metadata_recall_task and len(recall_results) > 3 else []
            # file_chunk는 이미 위에서 따로
            # 중복 content 방지
            def get_content(mem):
                if isinstance(mem, dict):
                    return mem.get('content', '')
                return str(mem)
            seen_contents = set()
            recall_texts = []
            recalled_memories = []
            # 각 전략별 2개씩 우선 추가
            for recall_group in [embedding_recall, belief_recall, emotion_recall, metadata_recall, file_chunk_recall]:
                added = 0
                for mem in recall_group:
                    content = get_content(mem)
                    if content and content not in seen_contents and content != '내용 없음':
                        recall_texts.append(content)
                        recalled_memories.append(mem)
                        seen_contents.add(content)
                        added += 1
                    if added >= 2:
                        break
            # 추가로 점수 상위 recall을 10개까지 더 반영 (중복 제외, break 없이)
            all_recalled = []
            for group in [embedding_recall, belief_recall, emotion_recall, metadata_recall, file_chunk_recall]:
                all_recalled.extend(group if isinstance(group, list) else [])
            scored_recalled = []
            for mem in all_recalled:
                sim = 0.0
                resonance = 0.0
                tag_overlap = 0
                if isinstance(mem, dict):
                    if 'similarity' in mem:
                        sim = mem['similarity']
                    resonance = mem.get('resonance_score', 0.0)
                    tag_overlap = len(set(mem.get('belief_tags', [])) & set(user_input.split()))
                score = sim + resonance + tag_overlap
                content = get_content(mem)
                if content and content not in seen_contents:
                    scored_recalled.append((score, mem))
                    seen_contents.add(content)
            scored_recalled.sort(key=lambda x: x[0], reverse=True)
            MAX_RECALL = 15  # 전체 최대 반영 개수
            for idx, (score, mem) in enumerate(scored_recalled):
                content = get_content(mem)
                if content and content != '내용 없음' and content not in recall_texts:
                    recall_texts.append(content)
                    recalled_memories.append(mem)
                if len(recall_texts) >= MAX_RECALL:
                    break
        except Exception as e:
            logger.error(f"❌ 분석/회상 준비 중 오류: {e}", exc_info=True)
            messages = []  # 예외 시에도 항상 정의
            recall_texts = []
            recalled_memories = []
        # recall은 반드시 await, analysis는 있으면 await, 없으면 이전 결과 사용
        t0 = time.perf_counter()
        if analysis_task:
            if recall_task is not None:
                analysis_result, recalled_memories2 = await asyncio.gather(analysis_task, recall_task)
                if not recalled_memories:
                    recalled_memories = recalled_memories2
            else:
                analysis_result = await analysis_task
        else:
            if recall_task is not None:
                recalled_memories2 = await recall_task
                if not recalled_memories:
                    recalled_memories = recalled_memories2
            analysis_result = self.last_analysis_results if hasattr(self, 'last_analysis_results') else {}
        # 날짜/요일 기반 회상 추가
        query_date_info = parse_date_info(user_input)
        date_recall_memories = []
        if query_date_info:
            # memory_manager에서 직접 메타데이터 기반 recall (예시)
            if hasattr(self.memory_manager, 'search_by_metadata'):
                date_recall_memories = await self.memory_manager.search_by_metadata(query_date_info)
            else:
                # fallback: recalled_memories에서 metadata에 date/weekday가 일치하는 것 우선 추출
                for mem in recalled_memories:
                    meta = mem.get('metadata', {})
                    if any(meta.get(k) == v for k, v in query_date_info.items() if k in ['date','weekday']):
                        date_recall_memories.append(mem)
        # date/weekday 일치 메모리가 있으면 답변에 반드시 반영
        if date_recall_memories:
            # 가장 최근 또는 첫 번째 관련 메모리 내용 우선
            def get_memory_text(mem):
                if not isinstance(mem, dict):
                    return '내용 없음'
                if isinstance(mem.get('content'), list):
                    return '내용 없음'
                if 'metadata' in mem and isinstance(mem['metadata'], dict):
                    meta_content = mem['metadata'].get('content')
                    if isinstance(meta_content, list):
                        return '내용 없음'
                if mem.get('content') and isinstance(mem.get('content'), str):
                    return mem['content']
                if 'metadata' in mem and isinstance(mem['metadata'], dict) and isinstance(mem['metadata'].get('content'), str):
                    return mem['metadata']['content']
                if mem.get('user_input'):
                    return mem['user_input']
                if mem.get('gpt_response'):
                    return mem['gpt_response']
                return '내용 없음'
            date_recall_texts = [get_memory_text(mem) for mem in date_recall_memories if get_memory_text(mem) != '내용 없음']
            if date_recall_texts:
                return {
                    "role": "EORA",
                    "response": f"요청하신 날짜/요일 관련 회상: {'; '.join(date_recall_texts)}",
                    "tasks": [],
                    "analysis": analysis_result,
                    "eai_analysis": eai_analysis_result,
                    "memories": date_recall_texts,
                    "truth": analysis_result.get("truth"),
                    "self_realization": analysis_result.get("self_realization"),
                }
        t1 = time.perf_counter()
        # 통찰(직감) 분석은 회상 결과를 받아서 실행
        if recalled_memories and self.insight_engine:
            try:
                insight_task = self.insight_engine.generate_insights(recalled_memories)
                insights = await insight_task
                if insights:
                    insight_text = "\n".join(insights)
            except Exception as e:
                logger.error(f"통찰(직감) 분석 오류: {e}", exc_info=True)
                insight_text = ""
        t2 = time.perf_counter()
        # 10턴마다 톤 분석
        if self.turn_count % 10 == 0:
            try:
                eora_response = self.last_gpt_response if self.last_gpt_response else ""
                tone_analysis_result = evaluate_eora_turn(user_input, eora_response, eora_response)
            except Exception as e:
                logger.error(f"[10턴 톤 분석] 오류: {e}", exc_info=True)
                tone_analysis_result = None
        t3 = time.perf_counter()
        # 타임 측정 코드 삭제
        # LLM 프롬프트 생성
        def get_memory_text(mem):
            if not isinstance(mem, dict):
                return '내용 없음'
            if isinstance(mem.get('content'), list):
                return '내용 없음'
            if 'metadata' in mem and isinstance(mem['metadata'], dict):
                meta_content = mem['metadata'].get('content')
                if isinstance(meta_content, list):
                    return '내용 없음'
            if mem.get('content') and isinstance(mem.get('content'), str):
                return mem['content']
            if 'metadata' in mem and isinstance(mem['metadata'], dict) and isinstance(mem['metadata'].get('content'), str):
                return mem['metadata']['content']
            if mem.get('user_input'):
                return mem['user_input']
            if mem.get('gpt_response'):
                return mem['gpt_response']
            return '내용 없음'
        # EAI 시스템 방향성/분석 활용 예시
        eai_direction = None
        if self.eai_system:
            eai_direction = self.eai_system.get_direction(user_input)
        # eai_direction을 프롬프트나 분석 결과에 반영 (예시)
        system_prompt = load_ai1_system_prompt()
        if eai_direction:
            system_prompt = f"[EAI 방향성] {eai_direction}\n" + system_prompt
        system_prompt = (
            "아래 [과거 대화 요약] 메시지는 참고하여, 필요하다고 판단되는 경우에만 답변에 반영하라. "
            "특히, 날씨/시간/장소/감정 등 맥락이 중요한 경우에는 과거 대화를 적극적으로 활용하라.\n"
           "아래 [과거 대화 요약] 사용자 질문이 1개 이상의 회상 답변을 요구 하는지 판단하여 대화에 필요하다고 판단되는 경우 1개 이상 3개까지 답변에 반영하라.\n "
            + system_prompt
        )
        messages = [{"role": "system", "content": system_prompt}]
        # 회상 정보 여러 개 추가, 중복 방지는 한 턴(한 번의 응답 생성) 내에서만 적용
        if recalled_memories:
            seen_memories = set()  # 이 턴에서만 중복 방지
            for i, mem in enumerate(recalled_memories[:10]):  # 원하는 개수만큼 추가 (10개 예시)
                content = get_memory_text(mem)
                if content and content != '내용 없음' and content not in seen_memories:
                    messages.append({"role": "system", "content": f"[과거 대화 요약] {content}"})
                    seen_memories.add(content)
        # 분석 결과 프롬프트에 추가 (user 메시지로, 중복 방지)
        truth = analysis_result.get("truth")
        if truth and truth not in [m["content"] for m in messages if m["role"] == "user"]:
            messages.append({"role": "user", "content": f"[진실 감각 분석]\n- {truth}"})
        self_realization = analysis_result.get("self_realization")
        if self_realization and self_realization not in [m["content"] for m in messages if m["role"] == "user"]:
            messages.append({"role": "user", "content": f"[자아실현적 성찰]\n- {self_realization}"})
        # EAI 분석 결과 추가 (user 메시지로, 중복 방지)
        if eai_analysis_result:
            try:
                formatted_eai = "\n".join([f"- {k}: {v}" for k, v in eai_analysis_result.items() if v])
                if formatted_eai and formatted_eai not in [m["content"] for m in messages if m["role"] == "user"]:
                    messages.append({"role": "user", "content": f"[EAI 시스템 분석 결과]\n{formatted_eai}"})
            except Exception as e:
                logger.error(f"EAI 결과 포맷팅 중 오류: {e}")
        # 통찰 결과 추가 (user 메시지로, 중복 방지)
        if insight_text and insight_text not in [m["content"] for m in messages if m["role"] == "user"]:
            messages.append({"role": "user", "content": f"[직감(통찰) 분석]\n{insight_text}"})
        # 마지막에 실제 사용자 입력 추가 (중복 방지)
        if user_input not in [m["content"] for m in messages if m["role"] == "user"]:
            messages.append({"role": "user", "content": user_input})
        # LLM API 호출 (timeout 최적화: 30초 → 12초)
        t4 = time.perf_counter()
        try:
            response = await self.client.chat.completions.create(model="gpt-4o", messages=messages, timeout=12)
            response_text = response.choices[0].message.content
            if self.turn_count % 10 == 0:
                messages2 = messages + [{"role": "system", "content": "[리마인드/톤 분석용 추가 메시지]"}]
                response2 = await self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages2, timeout=8)
        except asyncio.CancelledError:
            logger.error("❌ OpenAI API 호출이 취소되었습니다. (CancelledError)")
            return {
                "role": "EORA",
                "response": "요청이 취소되었습니다. 네트워크 상태 또는 시스템 상태를 확인해 주세요.",
                "tasks": [],
                "analysis": analysis_result,
                "eai_analysis": eai_analysis_result,
                "memories": [get_memory_text(mem) for mem in recalled_memories] if recalled_memories else [],
                "truth": truth,
                "self_realization": self_realization,
            }
        except Exception as e:
            logger.error(f"❌ OpenAI API 호출 중 오류 발생: {e}", exc_info=True)
            response_text = "죄송합니다, 응답 생성 중 오류가 발생했습니다."
        t5 = time.perf_counter()
        # 메모리 저장 및 상태 업데이트 (비동기 백그라운드)
        try:
            full_memory_metadata = {
                "user_input": user_input,
                "gpt_response": response_text,
                "emotion": analysis_result.get("emotion"),
                "belief_tags": analysis_result.get("belief_tags"),
                "event_score": analysis_result.get("event_score"),
                "recall_priority": analysis_result.get("recall_priority"),
                "emotional_intensity": analysis_result.get("emotional_intensity"),
                "resonance_score": analysis_result.get("resonance_score"),
                "intuition_vector": analysis_result.get("intuition_vector"),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "parent_id": analysis_result.get("parent_id"),
                "memory_id": str(uuid.uuid4()),
                "content": f"User: {user_input}\nEORA: {response_text}",
                **analysis_result
            }
            if tone_analysis_result:
                full_memory_metadata["tone_analysis"] = tone_analysis_result
            asyncio.create_task(self.memory_manager.store_memory(
                content=f"User: {user_input}\nEORA: {response_text}",
                metadata=full_memory_metadata
            ))
            # MemoryNode로 체인에 추가
            node = MemoryNode(
                user=user_input,
                gpt=response_text,
                emotion=analysis_result.get("emotion"),
                belief_tags=analysis_result.get("belief_tags", []),
                event_score=analysis_result.get("event_score", 0.0),
                recall_priority=analysis_result.get("recall_priority", 0.0),
                emotional_intensity=analysis_result.get("emotional_intensity", 0.0),
                resonance_score=analysis_result.get("resonance_score", 0.0),
                intuition_vector=analysis_result.get("intuition_vector", []),
                parent_id=analysis_result.get("parent_id"),
                source=analysis_result.get("source_type", "self")
            )
            memory_chain_manager.add_memory(node)
        except Exception as e:
            logger.error(f"❌ 메모리 저장/체인 추가 오류: {e}", exc_info=True)
        # 2. 회상: modular_recall_engine의 다양한 전략 병렬/조합 적용
        try:
            # 기본 recall (임베딩/키워드/감정/계보/빈도 등 종합)
            recalls = modular_recall_engine.recall_memories(user_input, top_n=3)
            # 추가 전략 예시 (필요시 병렬 gather)
            # story_recalls = modular_recall_engine.recall_by_story(node.memory_id, depth=3)
            # emotion_recalls = modular_recall_engine.recall_by_emotion("기쁨")
        except Exception as e:
            logger.error(f"❌ ModularRecallEngine 회상 오류: {e}", exc_info=True)
            recalls = []
        # 3. 회상 결과를 상위 계층(통찰/지혜 등)으로 전달
        try:
            if hasattr(self, 'insight_engine') and self.insight_engine:
                insight = await self.insight_engine.generate_insights([n.to_dict() for n in recalls] if recalls else [])
            else:
                insight = None
            if hasattr(self, 'wisdom_engine') and self.wisdom_engine:
                wise_response = await self.wisdom_engine.generate_wise_response([n.to_dict() for n in recalls] if recalls else [], {}, analysis_result.get("emotion"))
            else:
                wise_response = None
        except Exception as e:
            logger.error(f"❌ 상위 계층(통찰/지혜) 전달 오류: {e}", exc_info=True)
            insight = None
            wise_response = None
        # 4. 망각 자동화: 응답마다 fade_unused_memories 호출
        try:
            memory_chain_manager.fade_unused_memories(time_passed=1.0, irrelevance_factor=0.01)
        except Exception as e:
            logger.error(f"❌ 망각(fade_unused_memories) 오류: {e}", exc_info=True)
        # 마지막 대화 히스토리 저장
        self.last_user_input = user_input
        self.last_gpt_response = response_text
        self.dialogue_history_for_insight.append({"role": "user", "content": user_input})
        self.dialogue_history_for_insight.append({"role": "assistant", "content": response_text})
        if len(self.dialogue_history_for_insight) > 20:
            self.dialogue_history_for_insight = self.dialogue_history_for_insight[-20:]
        return {
            "role": "EORA",
            "response": response_text,
            "tasks": [],
            "analysis": analysis_result,
            "eai_analysis": eai_analysis_result,
            "memories": [get_memory_text(mem) for mem in recalled_memories] if recalled_memories else [],
            "truth": truth,
            "self_realization": self_realization,
        }

async def get_eora_ai(memory_manager=None) -> EORAAI:
    """EORA AI 인스턴스를 가져옵니다. (싱글톤)"""
    global _eora_ai_instance
    if _eora_ai_instance is None:
        # logger.info("글로벌 EORA AI 인스턴스가 존재하지 않아 새로 생성합니다.")
        if memory_manager is None:
            # logger.info("get_eora_ai 호출 시 memory_manager가 없어 새로 가져옵니다.")
            memory_manager = await get_memory_manager()
        _eora_ai_instance = EORAAI(memory_manager)
        await _eora_ai_instance.initialize()
    else:
        # logger.info("기존 EORA AI 인스턴스를 재사용합니다.")
        pass
    return _eora_ai_instance

def load_existing_session():
    """기존 세션 정보를 로드합니다 (예시)."""
    return None