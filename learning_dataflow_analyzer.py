#!/usr/bin/env python3
"""
학습 데이터 흐름 정밀 분석기
- 저장과 불러오기 과정의 각 단계를 상세히 추적
- 데이터 변환 과정 분석
- 필드 매핑 문제 진단
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LearningDataFlowAnalyzer:
    """학습 데이터 흐름 분석기"""
    
    def __init__(self):
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "storage_analysis": {},
            "retrieval_analysis": {},
            "field_mapping": {},
            "data_transformation": {},
            "compatibility_issues": []
        }
    
    async def analyze_complete_flow(self) -> Dict[str, Any]:
        """전체 데이터 흐름 분석"""
        logger.info("🔬 학습 데이터 흐름 정밀 분석 시작")
        logger.info("=" * 60)
        
        try:
            # 1. 저장 과정 분석
            await self._analyze_storage_process()
            
            # 2. 저장된 데이터 구조 분석
            await self._analyze_stored_data_structure()
            
            # 3. 검색 쿼리 분석
            await self._analyze_search_queries()
            
            # 4. 필드 매핑 문제 진단
            await self._diagnose_field_mapping()
            
            # 5. 호환성 문제 분석
            await self._analyze_compatibility_issues()
            
            # 6. 최종 권장사항 생성
            self._generate_recommendations()
            
        except Exception as e:
            logger.error(f"❌ 분석 중 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
        
        return self.analysis_results
    
    async def _analyze_storage_process(self):
        """저장 과정 분석"""
        logger.info("1️⃣ 저장 과정 분석")
        
        try:
            from mongodb_config import get_optimized_mongodb_connection
            from enhanced_learning_system import get_enhanced_learning_system
            
            client = get_optimized_mongodb_connection()
            learning_system = get_enhanced_learning_system(client)
            
            # 테스트 데이터
            test_content = "이것은 데이터 흐름 분석을 위한 테스트 내용입니다. Python 프로그래밍과 인공지능에 대한 내용을 포함합니다."
            test_filename = "dataflow_test.txt"
            test_category = "분석테스트"
            
            logger.info(f"📝 테스트 저장 시작: {test_filename}")
            
            # 저장 전 상태 확인
            db = learning_system.db
            before_count = db.memories.count_documents({"memory_type": "enhanced_learning"})
            
            # 저장 실행
            storage_result = await learning_system.learn_document(
                content=test_content,
                filename=test_filename,
                category=test_category
            )
            
            # 저장 후 상태 확인
            after_count = db.memories.count_documents({"memory_type": "enhanced_learning"})
            
            # 저장된 데이터 확인
            stored_memories = list(db.memories.find({
                "source_file": test_filename,
                "memory_type": "enhanced_learning"
            }))
            
            self.analysis_results["storage_analysis"] = {
                "success": storage_result.get("success", False),
                "error": storage_result.get("error"),
                "before_count": before_count,
                "after_count": after_count,
                "new_memories": len(stored_memories),
                "expected_chunks": storage_result.get("total_chunks", 0),
                "saved_memory_ids": storage_result.get("saved_memories", []),
                "storage_details": storage_result
            }
            
            if stored_memories:
                # 첫 번째 저장된 메모리의 구조 분석
                sample_memory = stored_memories[0]
                logger.info("📊 저장된 메모리 구조 분석:")
                
                for key, value in sample_memory.items():
                    if key != "_id":
                        value_type = type(value).__name__
                        value_preview = str(value)[:50] if len(str(value)) > 50 else str(value)
                        logger.info(f"   🔸 {key} ({value_type}): {value_preview}")
                
                self.analysis_results["storage_analysis"]["sample_structure"] = {
                    k: type(v).__name__ for k, v in sample_memory.items()
                }
            
            logger.info(f"✅ 저장 분석 완료 - {before_count} → {after_count} (+{after_count - before_count})")
            
        except Exception as e:
            logger.error(f"❌ 저장 과정 분석 실패: {e}")
            self.analysis_results["storage_analysis"]["error"] = str(e)
    
    async def _analyze_stored_data_structure(self):
        """저장된 데이터 구조 분석"""
        logger.info("\n2️⃣ 저장된 데이터 구조 분석")
        
        try:
            from mongodb_config import get_optimized_database
            
            db = get_optimized_database()
            memories = db.memories
            
            # 메모리 타입별 필드 분석
            memory_types = ["enhanced_learning", "document_chunk"]
            
            for memory_type in memory_types:
                logger.info(f"📋 {memory_type} 타입 분석:")
                
                # 샘플 데이터 조회
                sample = memories.find_one({"memory_type": memory_type})
                
                if sample:
                    fields = {}
                    for key, value in sample.items():
                        if key != "_id":
                            fields[key] = {
                                "type": type(value).__name__,
                                "exists": True,
                                "sample_value": str(value)[:30] if value else None
                            }
                    
                    self.analysis_results["field_mapping"][memory_type] = fields
                    
                    # 주요 필드 확인
                    important_fields = ["content", "response", "filename", "source_file", "category", "keywords", "tags"]
                    for field in important_fields:
                        exists = field in fields
                        logger.info(f"   {'✅' if exists else '❌'} {field}: {'존재' if exists else '없음'}")
                else:
                    logger.info(f"   ⚠️ {memory_type} 타입의 데이터가 없습니다")
                    self.analysis_results["field_mapping"][memory_type] = {}
            
        except Exception as e:
            logger.error(f"❌ 데이터 구조 분석 실패: {e}")
    
    async def _analyze_search_queries(self):
        """검색 쿼리 분석"""
        logger.info("\n3️⃣ 검색 쿼리 분석")
        
        try:
            from eora_memory_system import EORAMemorySystem
            
            memory_system = EORAMemorySystem()
            
            test_queries = [
                {"query": "분석테스트", "memory_type": "enhanced_learning"},
                {"query": "Python", "memory_type": "enhanced_learning"},
                {"query": "dataflow", "memory_type": "enhanced_learning"},
                {"query": "인공지능", "memory_type": None}  # 타입 제한 없음
            ]
            
            search_results = {}
            
            for test_case in test_queries:
                query = test_case["query"]
                memory_type = test_case["memory_type"]
                
                logger.info(f"🔍 검색 테스트: '{query}' (타입: {memory_type or '전체'})")
                
                try:
                    results = await memory_system.recall_learned_content(
                        query=query,
                        memory_type=memory_type,
                        limit=10
                    )
                    
                    search_results[f"{query}_{memory_type or 'all'}"] = {
                        "query": query,
                        "memory_type": memory_type,
                        "result_count": len(results),
                        "results": []
                    }
                    
                    logger.info(f"   📊 결과: {len(results)}개")
                    
                    # 결과 상세 분석
                    for i, result in enumerate(results[:3]):  # 최대 3개
                        result_analysis = {
                            "memory_type": result.get("memory_type"),
                            "has_content": "content" in result,
                            "has_response": "response" in result,
                            "has_filename": "filename" in result or "source_file" in result,
                            "has_category": "category" in result,
                            "relevance_score": result.get("relevance_score", 0)
                        }
                        
                        search_results[f"{query}_{memory_type or 'all'}"]["results"].append(result_analysis)
                        
                        content_field = "content" if "content" in result else "response"
                        content = result.get(content_field, "")[:40]
                        filename = result.get("filename", result.get("source_file", "unknown"))
                        
                        logger.info(f"     📄 결과 {i+1}: {filename} - {content}...")
                
                except Exception as e:
                    logger.error(f"   ❌ 검색 오류: {e}")
                    search_results[f"{query}_{memory_type or 'all'}"] = {"error": str(e)}
            
            self.analysis_results["retrieval_analysis"] = search_results
            
        except Exception as e:
            logger.error(f"❌ 검색 쿼리 분석 실패: {e}")
    
    async def _diagnose_field_mapping(self):
        """필드 매핑 문제 진단"""
        logger.info("\n4️⃣ 필드 매핑 문제 진단")
        
        try:
            # enhanced_learning과 document_chunk 간 필드 비교
            enhanced_fields = self.analysis_results["field_mapping"].get("enhanced_learning", {})
            document_fields = self.analysis_results["field_mapping"].get("document_chunk", {})
            
            # 필드 매핑 테이블
            field_mappings = {
                "content_field": {
                    "enhanced_learning": "response",
                    "document_chunk": "content",
                    "compatible": True
                },
                "filename_field": {
                    "enhanced_learning": "source_file",
                    "document_chunk": "filename",
                    "compatible": True
                },
                "keywords_field": {
                    "enhanced_learning": "tags",
                    "document_chunk": "keywords",
                    "compatible": True
                },
                "category_field": {
                    "enhanced_learning": "category",
                    "document_chunk": "category",
                    "compatible": True
                }
            }
            
            mapping_issues = []
            
            for mapping_name, mapping_info in field_mappings.items():
                enhanced_field = mapping_info["enhanced_learning"]
                document_field = mapping_info["document_chunk"]
                
                enhanced_exists = enhanced_field in enhanced_fields
                document_exists = document_field in document_fields
                
                logger.info(f"🔗 {mapping_name}:")
                logger.info(f"   enhanced_learning.{enhanced_field}: {'✅' if enhanced_exists else '❌'}")
                logger.info(f"   document_chunk.{document_field}: {'✅' if document_exists else '❌'}")
                
                if not enhanced_exists or not document_exists:
                    issue = f"{mapping_name}: 필드 누락 - enhanced:{enhanced_exists}, document:{document_exists}"
                    mapping_issues.append(issue)
                    self.analysis_results["compatibility_issues"].append(issue)
            
            self.analysis_results["data_transformation"]["field_mappings"] = field_mappings
            self.analysis_results["data_transformation"]["mapping_issues"] = mapping_issues
            
            if not mapping_issues:
                logger.info("✅ 필드 매핑에 문제가 없습니다")
            else:
                logger.warning(f"⚠️ {len(mapping_issues)}개의 필드 매핑 문제 발견")
            
        except Exception as e:
            logger.error(f"❌ 필드 매핑 진단 실패: {e}")
    
    async def _analyze_compatibility_issues(self):
        """호환성 문제 분석"""
        logger.info("\n5️⃣ 호환성 문제 분석")
        
        try:
            # 검색 결과 분석에서 호환성 문제 찾기
            retrieval_analysis = self.analysis_results["retrieval_analysis"]
            
            for search_key, search_data in retrieval_analysis.items():
                if "error" in search_data:
                    continue
                
                query = search_data.get("query")
                result_count = search_data.get("result_count", 0)
                
                # 검색 결과가 없는 경우 원인 분석
                if result_count == 0:
                    issue = f"검색어 '{query}' 결과 없음 - 필드 매핑 또는 데이터 저장 문제 가능성"
                    self.analysis_results["compatibility_issues"].append(issue)
                    logger.warning(f"⚠️ {issue}")
                
                # 결과는 있지만 관련성이 낮은 경우
                elif result_count > 0:
                    results = search_data.get("results", [])
                    if results:
                        avg_relevance = sum(r.get("relevance_score", 0) for r in results) / len(results)
                        if avg_relevance < 1.0:
                            issue = f"검색어 '{query}' 관련성 점수 낮음 ({avg_relevance:.2f}) - 검색 알고리즘 개선 필요"
                            self.analysis_results["compatibility_issues"].append(issue)
                            logger.warning(f"⚠️ {issue}")
            
            # 메모리 타입별 일관성 검사
            storage_analysis = self.analysis_results["storage_analysis"]
            expected_chunks = storage_analysis.get("expected_chunks", 0)
            new_memories = storage_analysis.get("new_memories", 0)
            
            if expected_chunks != new_memories:
                issue = f"저장 불일치 - 예상 청크: {expected_chunks}, 실제 저장: {new_memories}"
                self.analysis_results["compatibility_issues"].append(issue)
                logger.warning(f"⚠️ {issue}")
            
        except Exception as e:
            logger.error(f"❌ 호환성 문제 분석 실패: {e}")
    
    def _generate_recommendations(self):
        """권장사항 생성"""
        logger.info("\n6️⃣ 권장사항 생성")
        
        recommendations = []
        
        # 호환성 문제 기반 권장사항
        issues = self.analysis_results["compatibility_issues"]
        
        if any("필드 누락" in issue for issue in issues):
            recommendations.append({
                "priority": "HIGH",
                "category": "필드 매핑",
                "description": "EORA 메모리 시스템의 검색 쿼리에 enhanced_learning 필드 추가 필요",
                "action": "eora_memory_system.py의 recall_learned_content 함수에서 response, source_file, tags 필드 검색 조건 추가"
            })
        
        if any("결과 없음" in issue for issue in issues):
            recommendations.append({
                "priority": "HIGH",
                "category": "검색 알고리즘",
                "description": "저장된 데이터를 찾지 못하는 문제 해결 필요",
                "action": "검색 쿼리의 필드명과 실제 저장된 필드명 일치 확인"
            })
        
        if any("관련성 점수 낮음" in issue for issue in issues):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "검색 품질",
                "description": "검색 결과의 관련성 향상 필요",
                "action": "관련성 점수 계산 알고리즘 개선 및 가중치 조정"
            })
        
        if any("저장 불일치" in issue for issue in issues):
            recommendations.append({
                "priority": "HIGH",
                "category": "데이터 일관성",
                "description": "저장 과정에서 데이터 손실 발생",
                "action": "enhanced_learning_system.py의 저장 로직 점검 및 트랜잭션 처리 강화"
            })
        
        # 기본 권장사항
        if not issues:
            recommendations.append({
                "priority": "LOW",
                "category": "최적화",
                "description": "현재 시스템이 정상 작동 중이며 추가 최적화 가능",
                "action": "성능 모니터링 및 정기적인 인덱스 최적화"
            })
        
        self.analysis_results["recommendations"] = recommendations
        
        logger.info("💡 권장사항:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"   {i}. [{rec['priority']}] {rec['category']}: {rec['description']}")
            logger.info(f"      → {rec['action']}")
    
    def print_summary(self):
        """요약 보고서 출력"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 학습 데이터 흐름 분석 요약")
        logger.info("=" * 60)
        
        # 저장 상태
        storage = self.analysis_results["storage_analysis"]
        if storage.get("success"):
            logger.info(f"✅ 저장: 성공 ({storage.get('new_memories', 0)}개 메모리)")
        else:
            logger.info(f"❌ 저장: 실패 - {storage.get('error', '알 수 없는 오류')}")
        
        # 검색 상태
        retrieval = self.analysis_results["retrieval_analysis"]
        successful_searches = sum(1 for v in retrieval.values() if isinstance(v, dict) and v.get("result_count", 0) > 0)
        total_searches = len(retrieval)
        logger.info(f"🔍 검색: {successful_searches}/{total_searches}개 성공")
        
        # 호환성 문제
        issues_count = len(self.analysis_results["compatibility_issues"])
        if issues_count == 0:
            logger.info("✅ 호환성: 문제 없음")
        else:
            logger.info(f"⚠️ 호환성: {issues_count}개 문제 발견")
        
        # 권장사항
        recommendations = self.analysis_results["recommendations"]
        high_priority = sum(1 for r in recommendations if r["priority"] == "HIGH")
        logger.info(f"💡 권장사항: {len(recommendations)}개 (긴급: {high_priority}개)")
        
        logger.info("=" * 60)

async def main():
    """메인 실행 함수"""
    analyzer = LearningDataFlowAnalyzer()
    
    try:
        results = await analyzer.analyze_complete_flow()
        analyzer.print_summary()
        
        # 상세 결과를 JSON 파일로 저장
        output_file = f"learning_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"\n📄 상세 분석 결과가 {output_file}에 저장되었습니다.")
        
        # 종료 코드 결정
        critical_issues = sum(1 for r in results["recommendations"] if r["priority"] == "HIGH")
        if critical_issues == 0:
            sys.exit(0)  # 성공
        else:
            sys.exit(1)  # 문제 발견
        
    except Exception as e:
        logger.error(f"❌ 분석 실행 오류: {e}")
        sys.exit(2)

if __name__ == "__main__":
    print("🔬 학습 데이터 흐름 정밀 분석기")
    print("이 도구는 학습 데이터의 저장과 불러오기 과정을 단계별로 분석합니다.")
    print()
    
    asyncio.run(main())