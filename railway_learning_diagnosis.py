#!/usr/bin/env python3
"""
Railway 환경용 학습 기능 정밀 진단 도구
- 무한루프 방지를 위한 타임아웃 설정
- 정상 종료 보장
- 상세한 디버깅 정보 제공
"""

import asyncio
import sys
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """타임아웃 예외"""
    pass

class RailwayLearningDiagnosis:
    """Railway 환경용 학습 기능 진단 클래스"""
    
    def __init__(self, timeout_seconds: int = 300):  # 5분 타임아웃
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.timeout_occurred = False
        self.test_results = {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "mongodb_connection": False,
            "enhanced_learning_init": False,
            "eora_memory_init": False,
            "storage_test": False,
            "recall_test": False,
            "db_verification": False,
            "error_details": [],
            "success_details": [],
            "memory_counts": {},
            "test_memory_id": None
        }
    
    def _start_timeout_monitor(self):
        """타임아웃 모니터 시작 (Windows 호환)"""
        def timeout_monitor():
            time.sleep(self.timeout_seconds)
            if not self.timeout_occurred:
                self.timeout_occurred = True
                logger.error(f"⏰ 타임아웃 발생: {self.timeout_seconds}초 초과")
        
        timeout_thread = threading.Thread(target=timeout_monitor, daemon=True)
        timeout_thread.start()
    
    def _check_timeout(self):
        """타임아웃 체크"""
        if self.timeout_occurred:
            raise TimeoutError(f"테스트가 {self.timeout_seconds}초 타임아웃에 도달했습니다")
        if self.start_time and time.time() - self.start_time > self.timeout_seconds:
            self.timeout_occurred = True
            raise TimeoutError(f"테스트가 {self.timeout_seconds}초 타임아웃에 도달했습니다")
    
    async def run_diagnosis(self) -> Dict[str, Any]:
        """메인 진단 실행"""
        self.start_time = time.time()
        self.test_results["start_time"] = datetime.now().isoformat()
        
        try:
            # Windows 호환 타임아웃 모니터 시작
            self._start_timeout_monitor()
            
            logger.info("🚀 Railway 학습 기능 정밀 진단 시작")
            logger.info(f"⏰ 타임아웃: {self.timeout_seconds}초")
            logger.info("=" * 60)
            
            # 단계별 진단 실행
            await self._test_mongodb_connection()
            self._check_timeout()
            
            await self._test_enhanced_learning_system()
            self._check_timeout()
            
            await self._test_eora_memory_system()
            self._check_timeout()
            
            await self._test_storage_functionality()
            self._check_timeout()
            
            await self._test_recall_functionality()
            self._check_timeout()
            
            await self._verify_database_state()
            self._check_timeout()
            
            # 정리 작업
            await self._cleanup_test_data()
            
        except TimeoutError as e:
            logger.error(f"⏰ 타임아웃 발생: {e}")
            self.test_results["error_details"].append(f"TIMEOUT: {e}")
        except Exception as e:
            logger.error(f"❌ 진단 중 오류 발생: {e}")
            self.test_results["error_details"].append(f"ERROR: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
        finally:
            # 타임아웃 종료 표시
            self.timeout_occurred = True
            
            self.test_results["end_time"] = datetime.now().isoformat()
            self.test_results["duration"] = time.time() - self.start_time
            
            self._print_final_report()
        
        return self.test_results
    
    async def _test_mongodb_connection(self):
        """MongoDB 연결 테스트"""
        logger.info("1️⃣ MongoDB 연결 테스트")
        
        try:
            from mongodb_config import get_optimized_mongodb_connection, get_optimized_database
            
            # 연결 테스트
            client = get_optimized_mongodb_connection()
            if client is None:
                self.test_results["error_details"].append("MongoDB 클라이언트 연결 실패")
                return
            
            # 핑 테스트
            client.admin.command('ping')
            
            # 데이터베이스 접근 테스트
            db = get_optimized_database()
            if db is None:
                self.test_results["error_details"].append("데이터베이스 연결 실패")
                return
            
            # 컬렉션 확인
            collections = db.list_collection_names()
            
            self.test_results["mongodb_connection"] = True
            self.test_results["success_details"].append(f"MongoDB 연결 성공 - 컬렉션: {len(collections)}개")
            logger.info(f"✅ MongoDB 연결 성공 - {len(collections)}개 컬렉션")
            
        except Exception as e:
            self.test_results["error_details"].append(f"MongoDB 연결 실패: {e}")
            logger.error(f"❌ MongoDB 연결 실패: {e}")
    
    async def _test_enhanced_learning_system(self):
        """강화된 학습 시스템 테스트"""
        logger.info("\n2️⃣ 강화된 학습 시스템 테스트")
        
        try:
            from mongodb_config import get_optimized_mongodb_connection
            from enhanced_learning_system import get_enhanced_learning_system
            
            client = get_optimized_mongodb_connection()
            learning_system = get_enhanced_learning_system(client)
            
            if learning_system is None or learning_system.db is None:
                self.test_results["error_details"].append("강화된 학습 시스템 초기화 실패")
                return
            
            self.test_results["enhanced_learning_init"] = True
            self.test_results["success_details"].append("강화된 학습 시스템 초기화 성공")
            logger.info("✅ 강화된 학습 시스템 초기화 성공")
            
        except Exception as e:
            self.test_results["error_details"].append(f"강화된 학습 시스템 초기화 실패: {e}")
            logger.error(f"❌ 강화된 학습 시스템 초기화 실패: {e}")
    
    async def _test_eora_memory_system(self):
        """EORA 메모리 시스템 테스트"""
        logger.info("\n3️⃣ EORA 메모리 시스템 테스트")
        
        try:
            from eora_memory_system import EORAMemorySystem
            
            memory_system = EORAMemorySystem()
            
            if not memory_system.is_connected():
                self.test_results["error_details"].append("EORA 메모리 시스템 연결 실패")
                return
            
            self.test_results["eora_memory_init"] = True
            self.test_results["success_details"].append("EORA 메모리 시스템 초기화 성공")
            logger.info("✅ EORA 메모리 시스템 초기화 성공")
            
        except Exception as e:
            self.test_results["error_details"].append(f"EORA 메모리 시스템 초기화 실패: {e}")
            logger.error(f"❌ EORA 메모리 시스템 초기화 실패: {e}")
    
    async def _test_storage_functionality(self):
        """저장 기능 테스트"""
        logger.info("\n4️⃣ 저장 기능 테스트")
        
        try:
            from mongodb_config import get_optimized_mongodb_connection
            from enhanced_learning_system import get_enhanced_learning_system
            
            client = get_optimized_mongodb_connection()
            learning_system = get_enhanced_learning_system(client)
            
            # 테스트 데이터
            test_content = f"Railway 테스트 학습 내용 - {datetime.now().isoformat()}"
            test_filename = "railway_test.txt"
            test_category = "테스트"
            
            logger.info(f"📝 테스트 내용 저장 시도: {test_filename}")
            
            # 저장 실행
            result = await asyncio.wait_for(
                learning_system.learn_document(
                    content=test_content,
                    filename=test_filename,
                    category=test_category
                ),
                timeout=30  # 30초 타임아웃
            )
            
            if result.get("success"):
                self.test_results["storage_test"] = True
                self.test_results["test_memory_id"] = result.get("saved_memories", [])
                self.test_results["success_details"].append(
                    f"저장 성공 - 파일: {test_filename}, 청크: {result.get('total_chunks')}개"
                )
                logger.info(f"✅ 저장 성공 - {result.get('total_chunks')}개 청크")
            else:
                self.test_results["error_details"].append(f"저장 실패: {result.get('error')}")
                logger.error(f"❌ 저장 실패: {result.get('error')}")
            
        except asyncio.TimeoutError:
            self.test_results["error_details"].append("저장 작업 타임아웃")
            logger.error("❌ 저장 작업 30초 타임아웃")
        except Exception as e:
            self.test_results["error_details"].append(f"저장 기능 테스트 실패: {e}")
            logger.error(f"❌ 저장 기능 테스트 실패: {e}")
    
    async def _test_recall_functionality(self):
        """회상 기능 테스트"""
        logger.info("\n5️⃣ 회상 기능 테스트")
        
        if not self.test_results["storage_test"]:
            logger.warning("⚠️ 저장 테스트가 실패하여 회상 테스트를 건너뜁니다")
            return
        
        try:
            from eora_memory_system import EORAMemorySystem
            
            memory_system = EORAMemorySystem()
            
            # 여러 검색어로 테스트
            test_queries = ["Railway", "테스트", "학습"]
            recall_results = {}
            
            for query in test_queries:
                logger.info(f"🔍 '{query}' 검색 테스트")
                
                try:
                    # enhanced_learning 타입으로 검색
                    results = await asyncio.wait_for(
                        memory_system.recall_learned_content(
                            query=query,
                            memory_type="enhanced_learning",
                            limit=5
                        ),
                        timeout=15  # 15초 타임아웃
                    )
                    
                    recall_results[query] = len(results)
                    logger.info(f"   📊 '{query}' 검색 결과: {len(results)}개")
                    
                    # 결과 상세 분석
                    if results:
                        for i, result in enumerate(results[:2]):  # 최대 2개만
                            content = result.get('content', result.get('response', ''))
                            filename = result.get('filename', result.get('source_file', 'unknown'))
                            logger.info(f"     📄 결과 {i+1}: {filename} - {content[:30]}...")
                
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ '{query}' 검색 타임아웃")
                    recall_results[query] = -1
                except Exception as e:
                    logger.error(f"❌ '{query}' 검색 오류: {e}")
                    recall_results[query] = -1
            
            # 결과 평가
            successful_searches = sum(1 for count in recall_results.values() if count >= 0)
            total_results = sum(count for count in recall_results.values() if count > 0)
            
            if successful_searches > 0:
                self.test_results["recall_test"] = True
                self.test_results["success_details"].append(
                    f"회상 성공 - {successful_searches}/{len(test_queries)}개 검색어, 총 {total_results}개 결과"
                )
                logger.info(f"✅ 회상 성공 - {successful_searches}/{len(test_queries)}개 검색어")
            else:
                self.test_results["error_details"].append("모든 회상 검색 실패")
                logger.error("❌ 모든 회상 검색 실패")
            
        except Exception as e:
            self.test_results["error_details"].append(f"회상 기능 테스트 실패: {e}")
            logger.error(f"❌ 회상 기능 테스트 실패: {e}")
    
    async def _verify_database_state(self):
        """데이터베이스 상태 검증"""
        logger.info("\n6️⃣ 데이터베이스 상태 검증")
        
        try:
            from mongodb_config import get_optimized_database
            
            db = get_optimized_database()
            memories = db.memories
            
            # 메모리 타입별 카운트
            memory_types = ["enhanced_learning", "document_chunk"]
            
            for memory_type in memory_types:
                count = memories.count_documents({"memory_type": memory_type})
                self.test_results["memory_counts"][memory_type] = count
                logger.info(f"📊 {memory_type}: {count}개")
            
            # 테스트 데이터 확인
            test_memories = memories.count_documents({
                "memory_type": "enhanced_learning",
                "source_file": "railway_test.txt"
            })
            
            logger.info(f"🧪 테스트 메모리: {test_memories}개")
            
            if test_memories > 0 or sum(self.test_results["memory_counts"].values()) > 0:
                self.test_results["db_verification"] = True
                self.test_results["success_details"].append(f"DB 검증 성공 - 테스트 메모리: {test_memories}개")
                logger.info("✅ 데이터베이스 상태 검증 성공")
            else:
                self.test_results["error_details"].append("DB에 메모리가 저장되지 않음")
                logger.error("❌ DB에 메모리가 저장되지 않음")
            
        except Exception as e:
            self.test_results["error_details"].append(f"DB 상태 검증 실패: {e}")
            logger.error(f"❌ DB 상태 검증 실패: {e}")
    
    async def _cleanup_test_data(self):
        """테스트 데이터 정리"""
        logger.info("\n7️⃣ 테스트 데이터 정리")
        
        try:
            from mongodb_config import get_optimized_database
            
            db = get_optimized_database()
            memories = db.memories
            
            # 테스트 데이터 삭제
            delete_result = memories.delete_many({
                "$or": [
                    {"source_file": "railway_test.txt"},
                    {"filename": "railway_test.txt"},
                    {"metadata.test_flag": True}
                ]
            })
            
            logger.info(f"🗑️ 테스트 데이터 {delete_result.deleted_count}개 정리 완료")
            
        except Exception as e:
            logger.warning(f"⚠️ 테스트 데이터 정리 중 오류: {e}")
    
    def _print_final_report(self):
        """최종 보고서 출력"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 Railway 학습 기능 진단 최종 보고서")
        logger.info("=" * 60)
        
        # 전체 성공률
        total_tests = 6
        passed_tests = sum([
            self.test_results["mongodb_connection"],
            self.test_results["enhanced_learning_init"],
            self.test_results["eora_memory_init"],
            self.test_results["storage_test"],
            self.test_results["recall_test"],
            self.test_results["db_verification"]
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"⏱️ 실행 시간: {self.test_results['duration']:.2f}초")
        logger.info(f"✅ 성공률: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # 성공한 항목
        logger.info("\n🎉 성공한 테스트:")
        for detail in self.test_results["success_details"]:
            logger.info(f"   ✅ {detail}")
        
        # 실패한 항목
        if self.test_results["error_details"]:
            logger.info("\n❌ 실패한 테스트:")
            for detail in self.test_results["error_details"]:
                logger.info(f"   ❌ {detail}")
        
        # 메모리 통계
        if self.test_results["memory_counts"]:
            logger.info(f"\n📊 메모리 통계:")
            for memory_type, count in self.test_results["memory_counts"].items():
                logger.info(f"   📋 {memory_type}: {count}개")
        
        # 결론
        if success_rate >= 80:
            logger.info("\n🎯 결론: 학습 기능이 정상적으로 작동합니다!")
        elif success_rate >= 50:
            logger.info("\n⚠️ 결론: 일부 기능에 문제가 있습니다. 확인이 필요합니다.")
        else:
            logger.info("\n🚨 결론: 심각한 문제가 있습니다. 즉시 수정이 필요합니다.")
        
        logger.info("=" * 60)

async def main():
    """메인 실행 함수"""
    diagnosis = RailwayLearningDiagnosis(timeout_seconds=300)  # 5분 타임아웃
    
    try:
        results = await diagnosis.run_diagnosis()
        
        # 종료 코드 결정
        success_rate = sum([
            results["mongodb_connection"],
            results["enhanced_learning_init"],
            results["eora_memory_init"],
            results["storage_test"],
            results["recall_test"],
            results["db_verification"]
        ]) / 6 * 100
        
        if success_rate >= 80:
            sys.exit(0)  # 성공
        else:
            sys.exit(1)  # 실패
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ 사용자에 의해 진단이 중단되었습니다.")
        sys.exit(2)
    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(3)

if __name__ == "__main__":
    print("🚀 Railway 학습 기능 정밀 진단 도구")
    print("이 도구는 Railway 환경에서 학습 기능의 저장/불러오기를 정밀하게 분석합니다.")
    print("타임아웃이 설정되어 무한루프나 정지 상황을 방지합니다.")
    print()
    
    asyncio.run(main())