import numpy as np
from typing import List, Dict, Any, Tuple
import asyncio
from datetime import datetime, timedelta
import logging
from bson.objectid import ObjectId, InvalidId
import json
import os
import re
from asyncio import CancelledError

# 순환 참조 방지를 위해 typing.TYPE_CHECKING 사용
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aura_system.memory_manager import MemoryManagerAsync

from aura_system.vector_store import embed_text_async
# from aura_system.emotion_analyzer import analyze_emotion  # 순환 참조 방지를 위해 주석 처리
from aura_system.resonance_engine import calculate_resonance
from utils.serialization import safe_mongo_doc

# 로거 정의
logger = logging.getLogger(__name__)

class RecallEngine:
    def __init__(self, memory_manager: "MemoryManagerAsync"):
        """
        RecallEngine을 초기화합니다.
        
        Args:
            memory_manager (MemoryManagerAsync): 초기화된 메모리 관리자 인스턴스.
        """
        if not memory_manager or not memory_manager.is_initialized:
            raise ValueError("RecallEngine은 반드시 초기화된 MemoryManagerAsync 인스턴스가 필요합니다.")
            
        self.memory_manager = memory_manager
        self._cache = {}
        self._cache_size = 1000
        self._recall_history = []
        self._max_history = 20
        
        # 회상 품질 임계값 (정확도 향상을 위해 조정)
        self.quality_thresholds = {
            "semantic": 0.3,  # 의미적 유사도 (0.0 → 0.3)
            "temporal": 0.2,  # 시간적 관련성 (0.0 → 0.2)
            "emotional": 0.2,  # 감정적 연관성 (0.0 → 0.2)
            "contextual": 0.2  # 문맥적 관련성 (0.0 → 0.2)
        }
        
        # 회상 가중치 (정확도 향상을 위해 조정)
        self.recall_weights = {
            "semantic": 0.35,    # 의미적 유사도 (0.4 → 0.35)
            "temporal": 0.15,    # 시간적 관련성 (0.2 → 0.15)
            "emotional": 0.25,   # 감정적 연관성 (0.2 → 0.25)
            "contextual": 0.25   # 문맥적 관련성 (0.2 → 0.25)
        }

    def load_recall_triggers(self):
        """recall_triggers.json에서 트리거 키워드 목록을 로드합니다."""
        try:
            trigger_path = os.path.join(os.path.dirname(__file__), 'prompts', 'recall_triggers.json')
            with open(trigger_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # history_recall, content_recall_keywords, content_recall_pattern 모두 병합
            keywords = data.get('history_recall', []) + data.get('content_recall_keywords', [])
            pattern = data.get('content_recall_pattern', None)
            return keywords, pattern
        except Exception as e:
            logger.warning(f"트리거 파일 로드 실패: {e}")
            return [], None

    def check_triggers(self, user_input, keywords, pattern):
        """입력에 트리거 키워드 또는 패턴이 포함되어 있는지 검사"""
        if not user_input:
            return False
        for kw in keywords:
            if kw in user_input:
                return True
        if pattern:
            try:
                if re.search(pattern, user_input):
                    return True
            except Exception:
                pass
        return False

    def _parse_time_expression(self, query: str):
        """
        사용자 입력에서 시간 표현을 파싱해 (start, end) 날짜 범위를 반환
        예: '어제' → (today-1, today-1), '그제' → (today-2, today-2), '3일 전' → (today-3, today-3),
            '지난주' → (today-7, today-1), '오늘' → (today, today), '내일' → (today+1, today+1), '모레' → (today+2, today+2)
        """
        today = datetime.now()
        # 기본값: None (시간 필터 없음)
        start = end = None
        if '어제' in query:
            d = today - timedelta(days=1)
            start = end = d
        elif '그제' in query:
            d = today - timedelta(days=2)
            start = end = d
        elif '3일 전' in query:
            d = today - timedelta(days=3)
            start = end = d
        elif '지난주' in query:
            end = today - timedelta(days=1)
            start = today - timedelta(days=7)
        elif '오늘' in query:
            start = end = today
        elif '내일' in query:
            d = today + timedelta(days=1)
            start = end = d
        elif '모레' in query:
            d = today + timedelta(days=2)
            start = end = d
        return start, end

    async def recall(self, query: str, context: Dict[str, Any] = None, emotion: Dict[str, Any] = None, belief: Dict[str, Any] = None, wisdom: Dict[str, Any] = None, eora: Dict[str, Any] = None, system: Dict[str, Any] = None, limit: int = 3, distance_threshold: float = 1.2) -> List[Dict[str, Any]]:
        """
        8종 회상 시스템 - 정확도 향상 버전
        1. 키워드 기반 회상
        2. 임베딩 기반 회상
        3. 시퀀스 체인 회상
        4. 메타데이터 기반 회상
        5. 감정 기반 회상
        6. 트리거 기반 회상
        7. 빈도 통계 기반 회상
        8. 신념 기반 회상 (새로 추가)
        """
        try:
            # 임베딩 생성 (임베딩 기반 회상용)
            if not hasattr(self, '_embedding_cache'):
                self._embedding_cache = {}
            emb_key = (query, str(context))
            if emb_key in self._embedding_cache:
                query_embedding = self._embedding_cache[emb_key]
            else:
                try:
                    query_embedding = await embed_text_async(query)
                except CancelledError:
                    return []
                self._embedding_cache[emb_key] = query_embedding
                
            # context 정보 추출
            parent_id = context.get('parent_id') if context else None
            session_id = context.get('session_id') if context else None
            time_tag = context.get('time_tag') if context else None
            emotion_label = emotion.get('label') if emotion else None
            user_id = context.get('user_id') if context else None
            
            # 8가지 전략 병렬 실행 (정확도 향상)
            results = await asyncio.gather(
                self.recall_by_keywords(query, limit),
                self.recall_by_embedding(query_embedding, limit),
                self.recall_by_sequence_chain(parent_id, limit),
                self.recall_by_metadata(session_id, time_tag, limit),
                self.recall_by_emotion(emotion_label, limit),
                self.detect_trigger_and_recall(query, limit),
                self.recall_by_frequency_stats(user_id, limit),
                self.recall_by_belief(query, limit)  # 8번째 전략 추가
            )
            
            # 결과 통합(중복 제거, 최신순) + 망각/계보/유형/자기-타인/반사/명상 등 필터링
            seen = set()
            merged = []
            
            for group in results:
                for mem in group:
                    mem_id = str(mem.get('_id', ''))
                    
                    # 망각: fade_score가 0.8 이상(망각 임계값)이고 연결(parent_id, grandparent_id, origin_id)이 없고 감정 임팩트(emotional_intensity, resonance_score)가 낮으면 제외
                    if mem.get('fade_score', 0) is not None and float(mem.get('fade_score', 0)) >= 0.8:
                        if not (mem.get('parent_id') or mem.get('grandparent_id') or mem.get('origin_id')):
                            if float(mem.get('emotional_intensity') or 0) < 0.3 and float(mem.get('resonance_score') or 0) < 0.3:
                                continue  # 망각
                    
                    # 자기/타인 구분, reflex_tag, memory_type 등 활용(필요시)
                    # reflex_tag가 True면 즉시 반응(우선순위 높임)
                    if mem.get('reflex_tag'):
                        merged.insert(0, mem)
                        seen.add(mem_id)
                        continue
                        
                    if mem_id and mem_id not in seen:
                        merged.append(mem)
                        seen.add(mem_id)
            
            # 회상 품질 평가 및 필터링 (정확도 향상)
            if merged:
                scored_memories = await self._evaluate_recall_quality(
                    merged, query_embedding, emotion_label, context, query
                )
                # 품질 임계값을 통과한 메모리만 선택
                filtered_memories = []
                for memory, score in scored_memories:
                    if score >= 0.4:  # 품질 임계값 설정
                        filtered_memories.append(memory)
                
                if filtered_memories:
                    merged = filtered_memories
            
            # 회상 실패 시 유사 회상 보완 (정확도 향상)
            if not merged:
                # 유사 회상: 임베딩/키워드/감정 기반 recall_by_embedding 등 재시도
                similar = await self.recall_by_embedding(query_embedding, limit)
                merged = similar[:limit] if similar else []
                # 보조 메시지 추가(실제 응답 생성부에서 활용)
                for m in merged:
                    m['recall_failure_simulation'] = True
            
            # 명상 회상: 입력이 없을 때(또는 명상 트리거) 감정/공명 강한 기억 자발 회상
            if not query.strip():
                meditation = [m for m in merged if (float(m.get('emotional_intensity') or 0) > 0.7 or float(m.get('resonance_score') or 0) > 0.7)]
                merged = meditation[:limit] if meditation else merged
            
            # 최신순 정렬
            def _get_time_str(m):
                v = m.get('timestamp', m.get('created_at', m.get('metadata', {}).get('created_at', '')))
                if isinstance(v, str):
                    return v
                elif hasattr(v, 'isoformat'):
                    return v.isoformat()
                else:
                    return str(v)
            merged.sort(key=_get_time_str, reverse=True)
            
            logger.info(f"8종 회상 완료 - 쿼리: {query}, 결과: {len(merged)}개")
            return merged[:limit]
            
        except Exception as e:
            logger.error(f"recall_engine 8전략 recall 오류: {e}", exc_info=True)
            return []

    async def _search_candidates(self, query_embedding: List[float], emotion: str, context: Dict[str, Any], distance_threshold: float) -> List[Dict[str, Any]]:
        """FAISS와 MongoDB를 사용하여 회상 후보를 검색합니다."""
        try:
            # 1. FAISS를 이용한 벡터 검색
            if self.memory_manager.faiss_index is None or self.memory_manager.faiss_index.ntotal == 0:
                logger.warning("FAISS 인덱스가 준비되지 않아 후보 검색을 건너뜁니다.")
                return []
            
            search_k = max(100, 20) # 후보를 충분히 많이 뽑음
            if search_k > self.memory_manager.faiss_index.ntotal:
                search_k = self.memory_manager.faiss_index.ntotal

            distances, indices = self.memory_manager.faiss_index.search(np.array([query_embedding]), search_k)

            # 2. 임계값 기반 필터링 및 ID 추출
            found_doc_ids = []
            for i, dist in zip(indices[0], distances[0]):
                if i != -1 and dist < distance_threshold:
                    found_doc_ids.append(self.memory_manager.faiss_id_map[i])

            if not found_doc_ids:
                return []

            # 3. MongoDB에서 전체 문서 조회
            def _db_call():
                valid_ids = []
                for doc_id in found_doc_ids:
                    try:
                        valid_ids.append(ObjectId(doc_id))
                    except (InvalidId, TypeError):
                        logger.warning(f"잘못된 ObjectId 형식: {doc_id}")
                
                if not valid_ids: return []
                
                cursor = self.memory_manager.resource_manager.memories.find({"_id": {"$in": valid_ids}})
                return [safe_mongo_doc(doc) for doc in cursor]

            initial_candidates = await asyncio.to_thread(_db_call)

            # 4. 감정 및 문맥 기반 추가 필터링
            emotion_filtered = [
                cand for cand in initial_candidates
                if self._check_emotion_match(cand.get('metadata', {}), emotion)
            ]
            context_filtered = emotion_filtered
            # logger.info(f"후보 검색 완료: {len(context_filtered)}개의 최종 후보 발견 (세션/프로그램/주제 무관 전체 메모리)")
            return context_filtered
            
        except Exception as e:
            logger.error(f"후보 검색 중 오류 발생: {e}", exc_info=True)
            return []

    def _check_emotion_match(self, metadata: Dict[str, Any], target_emotion: str) -> bool:
        """감정 일치 여부 확인"""
        try:
            if "emotion" not in metadata:
                return True # 감정 정보가 없으면 통과
                
            result_emotion = metadata["emotion"]
            if result_emotion == target_emotion:
                return True
                
            # 감정 호환성 체크 (더 정교한 로직으로 개선 가능)
            compatible_emotions = {
                "joy": ["surprise"], "sadness": ["fear"], "anger": ["fear"],
                "fear": ["sadness", "anger"], "surprise": ["joy"]
            }
            
            return target_emotion in compatible_emotions.get(result_emotion, [])
            
        except Exception:
            return True # 오류 발생 시 필터링하지 않음

    def _check_context_match(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """문맥 일치 여부 확인"""
        try:
            if not context:
                return True
                
            # 주제 일치 확인 (metadata에 'topic' 또는 'tags'가 있다고 가정)
            if "topic" in context:
                meta_topics = metadata.get("topic") or metadata.get("tags", [])
                if meta_topics and context["topic"] not in meta_topics:
                    return False
            
            # 시간적 관련성 확인
            if "timestamp" in metadata and "current_time" in context:
                try:
                    # ISO 형식 문자열을 datetime 객체로 변환
                    result_time_str = metadata["timestamp"]
                    current_time_str = context["current_time"]
                    
                    result_time = datetime.fromisoformat(result_time_str.replace("Z", "+00:00"))
                    current_time = datetime.fromisoformat(current_time_str.replace("Z", "+00:00"))
                    
                    # 시간대 정보가 없는 경우 naive 객체로 만들어 비교
                    if result_time.tzinfo is None:
                       result_time = result_time.replace(tzinfo=None)
                    if current_time.tzinfo is None:
                       current_time = current_time.replace(tzinfo=None)

                    if (current_time - result_time) > timedelta(days=30):
                        return False
                except (ValueError, TypeError) as e:
                    logger.warning(f"시간 비교 중 오류 발생: {e}. metadata: {metadata.get('timestamp')}, context: {context.get('current_time')}")

            return True
            
        except Exception:
            return True # 오류 발생 시 필터링하지 않음

    # 회상 품질 평가 개선
    async def _evaluate_recall_quality(
        self, candidates: List[Dict[str, Any]], 
        query_embedding: List[float],
        emotion: str,
        context: Dict[str, Any],
        query: str = None,
        insight_ids: set = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """회상 품질 평가 (정확도 향상)"""
        try:
            scored_candidates = []
            
            for candidate in candidates:
                # 각 차원별 점수 계산
                semantic_score = await self._calculate_semantic_score(candidate, query_embedding)
                temporal_score = self._calculate_temporal_score(candidate)
                emotional_score = self._calculate_emotional_score(candidate, emotion)
                contextual_score = self._calculate_contextual_score(candidate, context)
                topic_score = self._calculate_topic_score(candidate, query) if query else 0.0
                
                # 가중 평균 계산 (정확도 향상을 위해 조정)
                total_score = (
                    semantic_score * self.recall_weights["semantic"] +
                    temporal_score * self.recall_weights["temporal"] +
                    emotional_score * self.recall_weights["emotional"] +
                    contextual_score * self.recall_weights["contextual"] +
                    topic_score * 0.1  # 토픽 점수 추가 가중치
                )
                
                # 품질 임계값 검사
                if self._check_quality_thresholds(semantic_score, temporal_score, emotional_score, contextual_score):
                    scored_candidates.append((candidate, total_score))
            
            # 점수순 정렬
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            return scored_candidates
            
        except Exception as e:
            logger.error(f"회상 품질 평가 오류: {e}")
            return [(candidate, 0.5) for candidate in candidates]

    async def _calculate_semantic_score(self, candidate: Dict[str, Any], query_embedding: List[float]) -> float:
        """의미적 유사도 계산 (정확도 향상)"""
        try:
            # 메모리에서 임베딩 추출
            candidate_embedding = None
            if "embedding" in candidate:
                candidate_embedding = candidate["embedding"]
            elif "metadata" in candidate and "embedding" in candidate["metadata"]:
                candidate_embedding = candidate["metadata"]["embedding"]
            
            if not candidate_embedding:
                return 0.0
                
            # 코사인 유사도 계산
            similarity = np.dot(query_embedding, candidate_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(candidate_embedding)
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"의미적 유사도 계산 오류: {e}")
            return 0.0

    def _calculate_temporal_score(self, candidate: Dict[str, Any]) -> float:
        """시간적 관련성 계산 (정확도 향상)"""
        try:
            # 메모리에서 시간 정보 추출
            timestamp = None
            if "timestamp" in candidate:
                timestamp = candidate["timestamp"]
            elif "created_at" in candidate:
                timestamp = candidate["created_at"]
            elif "metadata" in candidate and "created_at" in candidate["metadata"]:
                timestamp = candidate["metadata"]["created_at"]
            
            if not timestamp:
                return 0.5
                
            # 시간 파싱
            if isinstance(timestamp, str):
                candidate_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                candidate_time = timestamp
                
            current_time = datetime.now()
            
            # 시간 차이에 따른 점수 계산 (정확도 향상)
            time_diff = (current_time - candidate_time).total_seconds()
            if time_diff < 0:
                return 0.0
                
            # 지수 감소 함수로 시간 가중치 계산
            # 최근 7일: 높은 점수, 30일: 중간 점수, 90일: 낮은 점수
            score = np.exp(-time_diff / (7 * 24 * 3600))  # 7일 기준
            return float(score)
            
        except Exception as e:
            logger.error(f"시간적 관련성 계산 오류: {e}")
            return 0.5

    def _calculate_emotional_score(self, candidate: Dict[str, Any], target_emotion: str) -> float:
        """감정적 연관성 계산 (정확도 향상)"""
        try:
            if not target_emotion:
                return 0.5
                
            # 메모리에서 감정 정보 추출
            candidate_emotion = None
            if "emotion" in candidate:
                candidate_emotion = candidate["emotion"]
            elif "metadata" in candidate and "emotion" in candidate["metadata"]:
                candidate_emotion = candidate["metadata"]["emotion"]
            elif "metadata" in candidate and "emotion_label" in candidate["metadata"]:
                candidate_emotion = candidate["metadata"]["emotion_label"]
            
            if not candidate_emotion:
                return 0.5
                
            # 정확한 감정 매칭
            if candidate_emotion.lower() == target_emotion.lower():
                return 1.0
                
            # 감정 호환성 매트릭스 (정확도 향상)
            compatible_emotions = {
                "기쁨": ["놀람", "사랑"],
                "슬픔": ["두려움", "사랑"],
                "분노": ["두려움", "놀람"],
                "두려움": ["슬픔", "분노"],
                "놀람": ["기쁨", "분노"],
                "사랑": ["기쁨", "슬픔"]
            }
            
            # 호환성 점수 계산
            if target_emotion in compatible_emotions:
                if candidate_emotion in compatible_emotions[target_emotion]:
                    return 0.7
            
            return 0.3
            
        except Exception as e:
            logger.error(f"감정적 연관성 계산 오류: {e}")
            return 0.5

    def _calculate_contextual_score(self, candidate: Dict[str, Any], context: Dict[str, Any]) -> float:
        """문맥적 관련성 계산 (정확도 향상)"""
        try:
            if not context:
                return 0.5
                
            score = 0.5
            matches = 0
            total_checks = 0
            
            # 세션 ID 매칭
            if "session_id" in context and "metadata" in candidate:
                total_checks += 1
                if candidate["metadata"].get("session_id") == context["session_id"]:
                    score += 0.3
                    matches += 1
            
            # 사용자 ID 매칭
            if "user_id" in context and "metadata" in candidate:
                total_checks += 1
                if candidate["metadata"].get("user_id") == context["user_id"]:
                    score += 0.2
                    matches += 1
            
            # 토픽 매칭
            if "topic" in context and "metadata" in candidate:
                total_checks += 1
                if candidate["metadata"].get("topic") == context["topic"]:
                    score += 0.2
                    matches += 1
            
            # 매칭 비율에 따른 점수 조정
            if total_checks > 0:
                match_ratio = matches / total_checks
                score = score * match_ratio
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"문맥적 관련성 계산 오류: {e}")
            return 0.5

    def _calculate_topic_score(self, candidate: Dict[str, Any], query: str) -> float:
        """주제/키워드 일치 점수 계산 (정확도 향상)"""
        try:
            if not query:
                return 0.5
                
            # 메모리 내용 추출
            content = ""
            if "content" in candidate:
                content = candidate["content"]
            elif "message" in candidate:
                content = candidate["message"]
            elif "response" in candidate:
                content = candidate["response"]
            
            if not content:
                return 0.5
            
            # 키워드 매칭 (정확도 향상)
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            
            # 공통 단어 수 계산
            common_words = query_words.intersection(content_words)
            if not query_words:
                return 0.5
                
            # Jaccard 유사도 계산
            similarity = len(common_words) / len(query_words.union(content_words))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"주제 점수 계산 오류: {e}")
            return 0.5

    def _check_quality_thresholds(
        self,
        semantic_score: float,
        temporal_score: float,
        emotional_score: float,
        contextual_score: float
    ) -> bool:
        """품질 임계값 검사 (정확도 향상)"""
        try:
            # 각 차원별 임계값 검사
            if semantic_score < self.quality_thresholds["semantic"]:
                return False
            if temporal_score < self.quality_thresholds["temporal"]:
                return False
            if emotional_score < self.quality_thresholds["emotional"]:
                return False
            if contextual_score < self.quality_thresholds["contextual"]:
                return False
            
            # 종합 점수 검사
            total_score = (
                semantic_score * self.recall_weights["semantic"] +
                temporal_score * self.recall_weights["temporal"] +
                emotional_score * self.recall_weights["emotional"] +
                contextual_score * self.recall_weights["contextual"]
            )
            
            return total_score >= 0.4  # 종합 임계값
            
        except Exception as e:
            logger.error(f"품질 임계값 검사 오류: {e}")
            return True  # 오류 시 기본적으로 통과

    def _select_top_recalls(self, scored_candidates: List[Tuple[Dict[str, Any], float]], limit: int) -> List[Dict[str, Any]]:
        """상위 회상 선택"""
        try:
            # 점수 기준 정렬
            sorted_candidates = sorted(scored_candidates, key=lambda x: x[1], reverse=True)
            
            # 중복 제거
            unique_candidates = []
            seen_contents = set()
            
            for candidate, score in sorted_candidates:
                content = candidate.get("content", "")
                if content not in seen_contents:
                    seen_contents.add(content)
                    unique_candidates.append(candidate)
                    if len(unique_candidates) >= limit:
                        break
            
            return unique_candidates
            
        except Exception as e:
            print(f"상위 회상 선택 중 오류: {str(e)}")
            return []

    def _update_recall_history(self, recalls: List[Dict[str, Any]]):
        """회상 이력 업데이트"""
        try:
            for recall in recalls:
                self._recall_history.append({
                    "content": recall.get("content", ""),
                    "timestamp": datetime.now().isoformat(),
                    "score": recall.get("score", 0.0)
                })
            
            if len(self._recall_history) > self._max_history:
                self._recall_history = self._recall_history[-self._max_history:]
                
        except Exception as e:
            print(f"회상 이력 업데이트 중 오류: {str(e)}")

    def _update_cache(self, key: int, value: List[Dict[str, Any]]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
            
        except Exception as e:
            print(f"캐시 업데이트 중 오류: {str(e)}")

    # ① 키워드 기반 회상
    async def recall_by_keywords(self, user_input: str, limit: int = 3) -> list:
        keywords = user_input.split()
        regex = "|".join([re.escape(k) for k in keywords if len(k) > 1])
        if not regex:
            return []
        query = {"content": {"$regex": regex, "$options": "i"}}
        cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", -1)], limit=limit)
        return [doc for doc in cursor]

    # ② 임베딩 기반 회상 (기존 함수 활용)
    async def recall_by_embedding(self, embedding_vector, limit: int = 3) -> list:
        candidates = await self._search_candidates(embedding_vector, "중립", None, distance_threshold=0.7)
        return candidates[:limit] if candidates else []

    # ③ 스토리 기반 회상
    async def recall_by_sequence_chain(self, parent_id: str, limit: int = 3) -> list:
        if not parent_id:
            return []
        query = {"metadata.parent_id": parent_id}
        cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", 1)], limit=limit)
        return [doc for doc in cursor]

    # ④ 상황 기반 회상
    async def recall_by_metadata(self, session_id: str = None, time_tag: str = None, limit: int = 3) -> list:
        query = {}
        if session_id:
            query["metadata.session_id"] = session_id
        if time_tag:
            query["metadata.time_tag"] = time_tag
        if not query:
            return []
        cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", -1)], limit=limit)
        return [doc for doc in cursor]

    # ⑤ 감정 기반 회상
    async def recall_by_emotion(self, emotion_label: str, limit: int = 3) -> list:
        if not emotion_label:
            return []
        query = {"metadata.emotion_label": emotion_label}
        cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", -1)], limit=limit)
        return [doc for doc in cursor]

    # ⑥ 의도 기반 회상 (트리거)
    async def detect_trigger_and_recall(self, user_input: str, limit: int = 3) -> list:
        keywords, pattern = self.load_recall_triggers()
        if self.check_triggers(user_input, keywords, pattern):
            cursor = self.memory_manager.resource_manager.memories.find({}, sort=[("created_at", -1)], limit=limit)
            return [doc for doc in cursor]
        return []

    # ⑦ 빈도 기반 회상
    async def recall_by_frequency_stats(self, user_id: str, limit: int = 3) -> list:
        if not user_id:
            return []
        pipeline = [
            {"$match": {"metadata.user_id": user_id}},
            {"$group": {"_id": "$content", "count": {"$sum": 1}, "doc": {"$first": "$$ROOT"}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        results = list(self.memory_manager.resource_manager.memories.aggregate(pipeline))
        return [r["doc"] for r in results]

    # ⑧ 신념 기반 회상 (개선된 버전)
    async def recall_by_belief(self, user_input: str, limit: int = 3) -> list:
        """신념/키워드 기반 회상 (정확도 향상)"""
        try:
            # 사용자 입력에서 신념 관련 키워드 추출
            belief_keywords = self._extract_belief_keywords(user_input)
            if not belief_keywords:
                return []
            
            # 신념 태그가 포함된 메모리 검색 (정확도 향상)
            query = {"metadata.belief_tags": {"$in": belief_keywords}}
            cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", -1)], limit=limit)
            results = [doc for doc in cursor]
            
            # 신념 강도에 따른 추가 필터링
            if results:
                filtered_results = []
                for result in results:
                    belief_strength = result.get('metadata', {}).get('belief_strength', 0.5)
                    if belief_strength >= 0.3:  # 신념 강도 임계값
                        filtered_results.append(result)
                return filtered_results[:limit]
            
            return results
        except Exception as e:
            logger.error(f"신념 기반 회상 오류: {e}")
            return []

    # ⑨ 감정 분석 기반 회상 (개선된 버전)
    async def recall_by_emotion_analysis(self, user_input: str, limit: int = 3) -> list:
        """감정 분석 기반 회상 (정확도 향상)"""
        try:
            # 사용자 입력의 감정 분석 (개선된 키워드 기반)
            emotion = self._analyze_emotion_from_text(user_input)
            if not emotion or emotion == "중립":
                return []
            
            # 해당 감정이 포함된 메모리 검색
            query = {"metadata.emotion": emotion}
            cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", -1)], limit=limit)
            results = [doc for doc in cursor]
            
            # 감정 강도에 따른 추가 필터링
            if results:
                filtered_results = []
                for result in results:
                    emotion_intensity = result.get('metadata', {}).get('emotion_intensity', 0.5)
                    if emotion_intensity >= 0.4:  # 감정 강도 임계값
                        filtered_results.append(result)
                return filtered_results[:limit]
            
            return results
        except Exception as e:
            logger.error(f"감정 분석 기반 회상 오류: {e}")
            return []

    # ⑩ 맥락 기반 회상 (새로 추가)
    async def recall_by_context(self, user_input: str, context: Dict[str, Any] = None, limit: int = 3) -> list:
        """맥락 기반 회상 (새로운 전략)"""
        try:
            if not context:
                return []
            
            # 맥락 정보 추출
            session_id = context.get('session_id')
            user_id = context.get('user_id')
            topic = context.get('topic')
            
            query = {}
            if session_id:
                query["metadata.session_id"] = session_id
            if user_id:
                query["metadata.user_id"] = user_id
            if topic:
                query["metadata.topic"] = topic
            
            if not query:
                return []
            
            cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", -1)], limit=limit)
            return [doc for doc in cursor]
        except Exception as e:
            logger.error(f"맥락 기반 회상 오류: {e}")
            return []

    # ⑪ 시간 기반 회상 (새로 추가)
    async def recall_by_time_pattern(self, user_input: str, limit: int = 3) -> list:
        """시간 패턴 기반 회상 (새로운 전략)"""
        try:
            # 시간 표현 파싱
            start_time, end_time = self._parse_time_expression(user_input)
            if not start_time or not end_time:
                return []
            
            # 시간 범위 내 메모리 검색
            query = {
                "created_at": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
            
            cursor = self.memory_manager.resource_manager.memories.find(query, sort=[("created_at", -1)], limit=limit)
            return [doc for doc in cursor]
        except Exception as e:
            logger.error(f"시간 기반 회상 오류: {e}")
            return []

    def _extract_belief_keywords(self, text: str) -> list:
        """텍스트에서 신념 관련 키워드 추출 (개선된 버전)"""
        belief_keywords = [
            # 기본 신념 키워드
            "믿음", "신념", "가치", "원칙", "철학", "사상", "이념", "관념",
            "신뢰", "확신", "의심", "회의", "부정", "긍정", "낙관", "비관",
            "도덕", "윤리", "정의", "선", "악", "옳음", "틀림", "당연",
            "당연히", "분명히", "확실히", "틀림없이", "아마도", "어쩌면",
            
            # 확장된 신념 키워드 (정확도 향상)
            "절대", "절대적", "상대", "상대적", "보편", "보편적", "개별", "개별적",
            "객관", "객관적", "주관", "주관적", "합리", "합리적", "비합리", "비합리적",
            "논리", "논리적", "직관", "직관적", "경험", "경험적", "이론", "이론적",
            "실용", "실용적", "이상", "이상적", "현실", "현실적", "이념", "이념적"
        ]
        
        found_keywords = []
        text_lower = text.lower()
        for keyword in belief_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords

    def _analyze_emotion_from_text(self, text: str) -> str:
        """텍스트에서 감정 분석 (개선된 키워드 기반)"""
        emotion_keywords = {
            "기쁨": ["기쁘", "행복", "즐거", "신나", "좋", "만족", "감사", "웃", "즐겁", "신나", "좋아", "좋은", "좋다"],
            "슬픔": ["슬프", "우울", "속상", "아프", "힘들", "지치", "눈물", "울", "슬퍼", "우울해", "속상해"],
            "분노": ["화나", "짜증", "열받", "분노", "격분", "화", "열", "짜증나", "화나", "분노해"],
            "두려움": ["무서", "겁나", "불안", "걱정", "우려", "두려", "무섭", "겁", "불안해", "걱정해"],
            "놀람": ["놀라", "깜짝", "어이", "헐", "와", "대박", "놀랍", "깜짝", "어이쿠", "헐"],
            "사랑": ["사랑", "좋아", "그리워", "그립", "사랑해", "좋아해", "그리워해"],
            "중립": ["그냥", "보통", "일반", "평범", "보통", "그저", "단순", "평상"]
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            # 가장 높은 점수의 감정 반환
            return max(emotion_scores, key=emotion_scores.get)
        
        return "중립"

async def recall(query: str, context: Dict[str, Any] = None, limit: int = 3) -> List[Dict[str, Any]]:
    """간편 회상 함수"""
    # RecallEngine은 memory_manager가 필요하므로 임시로 빈 결과 반환
    return []

async def find_linked_memories(text: str, top_k: int = 5) -> list:
    """
    텍스트 내용과 메타데이터를 기반으로 연결된 기억들을 찾습니다.
    (memory_manager.py의 search_memories_by_content 와 유사하지만, 
     향후 체인 및 링크 분석을 위해 분리)
    """
    # 이 기능의 완전한 구현을 위해서는 memory_manager 인스턴스가 필요합니다.
    # 현재 구조에서는 직접 접근이 어려우므로, 임시로 get_memory_manager를 호출합니다.
    from aura_system.memory_manager import get_memory_manager
    
    try:
        memory_manager = await get_memory_manager()
        if not memory_manager or not memory_manager.is_initialized:
            # logger가 없으므로 print 사용
            print("Warning: Memory manager is not available in find_linked_memories.")
            return []
            
        # 1. 내용 기반 검색
        content_matches = await memory_manager.search_memories_by_content(text, top_k=top_k)

        # 2. 메타데이터(chain_id 등) 기반 검색 (추가 구현 필요)
        # 예시: text에서 chain_id를 추출하고 해당 체인의 모든 기억을 가져오는 로직
        
        # 여기서는 우선 내용 기반 검색 결과만 반환
        return content_matches

    except Exception as e:
        print(f"Error in find_linked_memories: {e}")
        return [] 