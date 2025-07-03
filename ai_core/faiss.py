"""
ai_core.faiss
- FAISS 관련 클래스와 함수 모듈
"""

import os
import json
import logging
import numpy as np
import faiss
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class FaissIndex:
    """FAISS 인덱스 클래스"""
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = {}
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> bool:
        """벡터 추가
        
        Args:
            vectors (np.ndarray): 벡터 배열
            metadata (List[Dict[str, Any]]): 메타데이터 리스트
            
        Returns:
            bool: 성공 여부
        """
        try:
            if len(vectors) != len(metadata):
                raise ValueError("벡터와 메타데이터의 길이가 일치하지 않습니다.")
            
            start_id = len(self.metadata)
            self.index.add(vectors)
            
            for i, meta in enumerate(metadata):
                self.metadata[start_id + i] = meta
            
            return True
        except Exception as e:
            logger.error(f"⚠️ 벡터 추가 실패: {str(e)}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """벡터 검색
        
        Args:
            query_vector (np.ndarray): 쿼리 벡터
            k (int): 검색 결과 수
            
        Returns:
            Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]: (거리, 인덱스, 메타데이터)
        """
        try:
            distances, indices = self.index.search(query_vector.reshape(1, -1), k)
            metadata = [self.metadata.get(idx, {}) for idx in indices[0]]
            return distances[0], indices[0], metadata
        except Exception as e:
            logger.error(f"⚠️ 벡터 검색 실패: {str(e)}")
            return np.array([]), np.array([]), []
    
    def save(self, path: str) -> bool:
        """인덱스 저장
        
        Args:
            path (str): 저장 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 인덱스 저장
            index_path = os.path.join(path, 'index.faiss')
            faiss.write_index(self.index, index_path)
            
            # 메타데이터 저장
            metadata_path = os.path.join(path, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            logger.error(f"⚠️ 인덱스 저장 실패: {str(e)}")
            return False
    
    def load(self, path: str) -> bool:
        """인덱스 로드
        
        Args:
            path (str): 로드 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 인덱스 로드
            index_path = os.path.join(path, 'index.faiss')
            self.index = faiss.read_index(index_path)
            
            # 메타데이터 로드
            metadata_path = os.path.join(path, 'metadata.json')
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            return True
        except Exception as e:
            logger.error(f"⚠️ 인덱스 로드 실패: {str(e)}")
            return False

def create_index(dimension: int = 1536) -> FaissIndex:
    """인덱스 생성
    
    Args:
        dimension (int): 벡터 차원
        
    Returns:
        FaissIndex: FAISS 인덱스 객체
    """
    return FaissIndex(dimension)

def load_index(path: str) -> Optional[FaissIndex]:
    """인덱스 로드
    
    Args:
        path (str): 로드 경로
        
    Returns:
        Optional[FaissIndex]: FAISS 인덱스 객체
    """
    try:
        index = FaissIndex()
        if index.load(path):
            return index
        return None
    except Exception as e:
        logger.error(f"⚠️ 인덱스 로드 실패: {str(e)}")
        return None

def save_index(index: FaissIndex, path: str) -> bool:
    """인덱스 저장
    
    Args:
        index (FaissIndex): FAISS 인덱스 객체
        path (str): 저장 경로
        
    Returns:
        bool: 성공 여부
    """
    return index.save(path)

def search_similar(index: FaissIndex, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
    """유사 벡터 검색
    
    Args:
        index (FaissIndex): FAISS 인덱스 객체
        query_vector (np.ndarray): 쿼리 벡터
        k (int): 검색 결과 수
        
    Returns:
        List[Dict[str, Any]]: 검색 결과 메타데이터
    """
    _, _, metadata = index.search(query_vector, k)
    return metadata 