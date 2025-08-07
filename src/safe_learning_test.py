#!/usr/bin/env python3
"""
안전한 학습 기능 테스트 - 확실한 종료 보장
- 단계별 타임아웃 설정
- 강제 종료 메커니즘
- 진행 상황 실시간 출력
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class SafeLearningTest:
    """안전한 학습 기능 테스트 클래스"""
    
    def __init__(self):
        self.start_time = time.time()
        self.max_duration = 120  # 2분 최대 실행 시간
        self.step_timeout = 30   # 각 단계별 30초 타임아웃
        self.results = {}
        
    def check_time_limit(self, step_name: str):
        """시간 제한 체크"""
        elapsed = time.time() - self.start_time
        if elapsed > self.max_duration:
            logger.error(f"⏰ 전체 시간 제한 초과: {elapsed:.1f}초 > {self.max_duration}초")
            self.force_exit(f"시간 제한 초과 at {step_name}")
        
        logger.info(f"⏱️ 경과 시간: {elapsed:.1f}초 / {self.max_duration}초")
    
    def force_exit(self, reason: str):
        """강제 종료"""
        logger.error(f"🚨 강제 종료: {reason}")
        self.print_results()
        sys.exit(1)
    
    async def run_safe_test(self):
        """안전한 테스트 실행"""
        logger.info("🔒 안전한 학습 기능 테스트 시작")
        logger.info(f"⏰ 최대 실행 시간: {self.max_duration}초")
        logger.info(f"⚡ 단계별 타임아웃: {self.step_timeout}초")
        logger.info("=" * 50)
        
        try:
            # 1단계: MongoDB 연결 테스트
            await self.test_mongodb_connection()
            
            # 2단계: 학습 시스템 초기화 테스트
            await self.test_learning_system_init()
            
            # 3단계: 저장 기능 테스트
            await self.test_storage_function()
            
            # 4단계: 불러오기 기능 테스트
            await self.test_recall_function()
            
            # 5단계: 정리
            await self.cleanup_test_data()
            
            logger.info("✅ 모든 테스트 완료!")
            self.print_results()
            
        except asyncio.TimeoutError as e:
            logger.error(f"⏰ 타임아웃 발생: {e}")
            self.force_exit("asyncio 타임아웃")
        except Exception as e:
            logger.error(f"❌ 테스트 오류: {e}")
            self.print_results()
            sys.exit(1)
        finally:
            # 확실한 종료
            elapsed = time.time() - self.start_time
            logger.info(f"🏁 테스트 종료 - 총 소요 시간: {elapsed:.1f}초")
    
    async def test_mongodb_connection(self):
        """MongoDB 연결 테스트"""
        step_name = "MongoDB 연결"
        logger.info(f"1️⃣ {step_name} 테스트 시작")
        self.check_time_limit(step_name)
        
        try:
            # 타임아웃과 함께 실행
            result = await asyncio.wait_for(
                self._do_mongodb_test(),
                timeout=self.step_timeout
            )
            
            self.results["mongodb_connection"] = result
            logger.info(f"✅ {step_name} 완료: {result}")
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ {step_name} 타임아웃 ({self.step_timeout}초)")
            self.results["mongodb_connection"] = False
            raise
        except Exception as e:
            logger.error(f"❌ {step_name} 실패: {e}")
            self.results["mongodb_connection"] = False
            raise
    
    async def _do_mongodb_test(self):
        """실제 MongoDB 테스트 수행"""
        from mongodb_config import get_optimized_mongodb_connection, get_optimized_database
        
        # 연결 테스트
        client = get_optimized_mongodb_connection()
        if client is None:
            return False
        
        # 핑 테스트
        client.admin.command('ping')
        
        # 데이터베이스 테스트
        db = get_optimized_database()
        if db is None:
            return False
        
        # 컬렉션 확인
        collections = db.list_collection_names()
        logger.info(f"📋 발견된 컬렉션: {len(collections)}개")
        
        return True
    
    async def test_learning_system_init(self):
        """학습 시스템 초기화 테스트"""
        step_name = "학습 시스템 초기화"
        logger.info(f"2️⃣ {step_name} 테스트 시작")
        self.check_time_limit(step_name)
        
        try:
            result = await asyncio.wait_for(
                self._do_learning_init_test(),
                timeout=self.step_timeout
            )
            
            self.results["learning_init"] = result
            logger.info(f"✅ {step_name} 완료: {result}")
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ {step_name} 타임아웃 ({self.step_timeout}초)")
            self.results["learning_init"] = False
            raise
        except Exception as e:
            logger.error(f"❌ {step_name} 실패: {e}")
            self.results["learning_init"] = False
            raise
    
    async def _do_learning_init_test(self):
        """실제 학습 시스템 초기화 테스트"""
        from mongodb_config import get_optimized_mongodb_connection
        from enhanced_learning_system import get_enhanced_learning_system
        
        client = get_optimized_mongodb_connection()
        learning_system = get_enhanced_learning_system(client)
        
        if learning_system is None or learning_system.db is None:
            return False
        
        # EORA 메모리 시스템도 테스트
        from eora_memory_system import EORAMemorySystem
        memory_system = EORAMemorySystem()
        
        if not memory_system.is_connected():
            return False
        
        return True
    
    async def test_storage_function(self):
        """저장 기능 테스트"""
        step_name = "저장 기능"
        logger.info(f"3️⃣ {step_name} 테스트 시작")
        self.check_time_limit(step_name)
        
        try:
            result = await asyncio.wait_for(
                self._do_storage_test(),
                timeout=self.step_timeout
            )
            
            self.results["storage"] = result
            logger.info(f"✅ {step_name} 완료: {result}")
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ {step_name} 타임아웃 ({self.step_timeout}초)")
            self.results["storage"] = False
            raise
        except Exception as e:
            logger.error(f"❌ {step_name} 실패: {e}")
            self.results["storage"] = False
            raise
    
    async def _do_storage_test(self):
        """실제 저장 테스트 수행"""
        from mongodb_config import get_optimized_mongodb_connection
        from enhanced_learning_system import get_enhanced_learning_system
        
        client = get_optimized_mongodb_connection()
        learning_system = get_enhanced_learning_system(client)
        
        # 테스트 데이터
        test_content = f"안전 테스트 학습 내용 - {datetime.now().isoformat()}"
        test_filename = "safe_test.txt"
        test_category = "안전테스트"
        
        logger.info(f"📝 테스트 내용 저장: {test_filename}")
        
        # 저장 실행
        result = await learning_system.learn_document(
            content=test_content,
            filename=test_filename,
            category=test_category
        )
        
        success = result.get("success", False)
        if success:
            chunks = result.get("total_chunks", 0)
            saved = result.get("saved_memories", [])
            logger.info(f"💾 저장 성공: {chunks}개 청크, {len(saved) if isinstance(saved, list) else 0}개 메모리")
            self.results["test_memory_info"] = {
                "filename": test_filename,
                "chunks": chunks,
                "saved_count": len(saved) if isinstance(saved, list) else 0
            }
        else:
            logger.error(f"💾 저장 실패: {result.get('error')}")
        
        return success
    
    async def test_recall_function(self):
        """불러오기 기능 테스트"""
        step_name = "불러오기 기능"
        logger.info(f"4️⃣ {step_name} 테스트 시작")
        self.check_time_limit(step_name)
        
        if not self.results.get("storage", False):
            logger.warning("⚠️ 저장 테스트가 실패하여 불러오기 테스트를 건너뜁니다")
            self.results["recall"] = False
            return
        
        try:
            result = await asyncio.wait_for(
                self._do_recall_test(),
                timeout=self.step_timeout
            )
            
            self.results["recall"] = result
            logger.info(f"✅ {step_name} 완료: {result}")
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ {step_name} 타임아웃 ({self.step_timeout}초)")
            self.results["recall"] = False
            raise
        except Exception as e:
            logger.error(f"❌ {step_name} 실패: {e}")
            self.results["recall"] = False
            raise
    
    async def _do_recall_test(self):
        """실제 불러오기 테스트 수행"""
        from eora_memory_system import EORAMemorySystem
        
        memory_system = EORAMemorySystem()
        
        # 테스트 검색어들
        test_queries = ["안전테스트", "safe_test", "학습"]
        total_found = 0
        
        for query in test_queries:
            logger.info(f"🔍 '{query}' 검색 테스트")
            
            try:
                # enhanced_learning 타입으로 검색
                results = await memory_system.recall_learned_content(
                    query=query,
                    memory_type="enhanced_learning",
                    limit=5
                )
                
                found = len(results)
                total_found += found
                logger.info(f"   📊 '{query}' 검색 결과: {found}개")
                
                # 결과 상세 확인
                if results:
                    for i, result in enumerate(results[:2]):  # 최대 2개만
                        content = result.get('content', result.get('response', ''))
                        filename = result.get('filename', result.get('source_file', 'unknown'))
                        logger.info(f"     📄 결과 {i+1}: {filename} - {content[:30]}...")
                
            except Exception as e:
                logger.error(f"   ❌ '{query}' 검색 오류: {e}")
        
        success = total_found > 0
        logger.info(f"🎯 전체 검색 결과: {total_found}개 발견")
        return success
    
    async def cleanup_test_data(self):
        """테스트 데이터 정리"""
        step_name = "데이터 정리"
        logger.info(f"5️⃣ {step_name} 시작")
        self.check_time_limit(step_name)
        
        try:
            result = await asyncio.wait_for(
                self._do_cleanup(),
                timeout=self.step_timeout
            )
            
            self.results["cleanup"] = result
            logger.info(f"✅ {step_name} 완료: {result}")
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ {step_name} 타임아웃 ({self.step_timeout}초)")
            self.results["cleanup"] = False
        except Exception as e:
            logger.error(f"❌ {step_name} 실패: {e}")
            self.results["cleanup"] = False
    
    async def _do_cleanup(self):
        """실제 정리 작업 수행"""
        from mongodb_config import get_optimized_database
        
        db = get_optimized_database()
        memories = db.memories
        
        # 테스트 데이터 삭제
        delete_result = memories.delete_many({
            "$or": [
                {"source_file": "safe_test.txt"},
                {"filename": "safe_test.txt"},
                {"category": "안전테스트"}
            ]
        })
        
        deleted_count = delete_result.deleted_count
        logger.info(f"🗑️ 테스트 데이터 {deleted_count}개 정리 완료")
        
        return True
    
    def print_results(self):
        """결과 출력"""
        logger.info("\n" + "=" * 50)
        logger.info("📊 안전한 학습 기능 테스트 결과")
        logger.info("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for v in self.results.values() if v)
        
        logger.info(f"⏱️ 총 실행 시간: {time.time() - self.start_time:.1f}초")
        logger.info(f"✅ 성공률: {passed_tests}/{total_tests} ({(passed_tests/total_tests*100):.1f}%)")
        
        for test_name, result in self.results.items():
            status = "✅ 성공" if result else "❌ 실패"
            logger.info(f"   {test_name}: {status}")
        
        # 테스트 메모리 정보
        if "test_memory_info" in self.results:
            info = self.results["test_memory_info"]
            logger.info(f"📄 테스트 파일: {info['filename']}")
            logger.info(f"📊 생성된 청크: {info['chunks']}개")
            logger.info(f"💾 저장된 메모리: {info['saved_count']}개")
        
        # 최종 진단
        if passed_tests >= total_tests * 0.8:  # 80% 이상 성공
            logger.info("\n🎉 결론: 학습 기능이 정상적으로 작동합니다!")
        elif passed_tests >= total_tests * 0.5:  # 50% 이상 성공
            logger.info("\n⚠️ 결론: 일부 기능에 문제가 있습니다.")
        else:
            logger.info("\n🚨 결론: 심각한 문제가 있습니다.")
        
        logger.info("=" * 50)

async def main():
    """메인 실행 함수"""
    test = SafeLearningTest()
    
    try:
        await test.run_safe_test()
        
        # 성공률에 따른 종료 코드
        passed = sum(1 for v in test.results.values() if v)
        total = len(test.results)
        
        if passed >= total * 0.8:
            sys.exit(0)  # 성공
        else:
            sys.exit(1)  # 실패
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
        test.print_results()
        sys.exit(2)
    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류: {e}")
        test.print_results()
        sys.exit(3)
    finally:
        # 강제 종료 타이머
        import threading
        def force_shutdown():
            time.sleep(10)  # 10초 후 강제 종료
            logger.error("🚨 강제 종료 타이머 작동")
            os._exit(1)
        
        shutdown_timer = threading.Thread(target=force_shutdown, daemon=True)
        shutdown_timer.start()

if __name__ == "__main__":
    print("🔒 안전한 학습 기능 테스트")
    print("이 테스트는 확실한 종료를 보장하며 무한루프를 방지합니다.")
    print("최대 2분 실행 후 자동 종료됩니다.")
    print()
    
    asyncio.run(main())