"""
utils_lightweight.py

EORA 시스템용 경량화된 유틸리티 모듈
- 외부 의존성 최소화 (numpy, hashlib만 사용)
- 간단한 임베딩, 유사도 계산, 감정 분석 기능
- MongoDB나 대형 라이브러리 없이 동작
"""

import numpy as np
import hashlib
import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# 감정 키워드 사전 (간단한 감정 분석용)
EMOTION_KEYWORDS = {
    "joy": ["기쁨", "행복", "즐거움", "웃음", "환희", "만족", "희망"],
    "sadness": ["슬픔", "우울", "절망", "비통", "허전", "외로움", "실망"],
    "anger": ["분노", "화남", "짜증", "열받음", "격분", "증오", "원망"],
    "fear": ["두려움", "공포", "불안", "걱정", "겁", "무서움", "긴장"],
    "surprise": ["놀람", "충격", "의외", "예상밖", "깜짝", "놀라움"],
    "disgust": ["역겨움", "혐오", "싫음", "구역질", "메스껍", "지겨움"],
    "curious": ["호기심", "궁금", "관심", "의문", "탐구", "알고싶"],
    "love": ["사랑", "애정", "따뜻함", "정", "애착", "그리움"],
    "neutral": ["평온", "차분", "무덤덤", "보통", "일반", "평범"]
}

def simple_embed(text: str) -> List[float]:
    """
    간단한 텍스트 임베딩 생성 (해시 기반)
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        List[float]: 128차원 임베딩 벡터
    """
    try:
        if not text or not isinstance(text, str):
            return [0.0] * 128
            
        # 텍스트 정규화
        text = text.lower().strip()
        if not text:
            return [0.0] * 128
            
        # 해시 기반 임베딩 생성
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # 128비트 해시를 128차원 벡터로 변환
        vector = []
        for i in range(0, 32, 2):  # 32자리 hex를 16개 쌍으로
            hex_pair = hash_hex[i:i+2]
            value = int(hex_pair, 16) / 255.0  # 0-1 범위로 정규화
            vector.append(value)
            
        # 16차원을 128차원으로 확장 (반복 패턴 사용)
        extended_vector = []
        for i in range(8):  # 8번 반복
            for val in vector:
                extended_vector.append(val * (0.8 + 0.2 * i))  # 약간의 변화 추가
                
        return extended_vector[:128]  # 정확히 128차원 보장
        
    except Exception as e:
        logger.error(f"임베딩 생성 실패: {str(e)}")
        return [0.0] * 128

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    코사인 유사도 계산
    
    Args:
        vec1 (List[float]): 첫 번째 벡터
        vec2 (List[float]): 두 번째 벡터
        
    Returns:
        float: 코사인 유사도 (0-1 범위)
    """
    try:
        if not vec1 or not vec2:
            return 0.0
            
        # numpy 배열로 변환
        v1 = np.array(vec1, dtype=float)
        v2 = np.array(vec2, dtype=float)
        
        # 차원 맞추기
        min_dim = min(len(v1), len(v2))
        v1 = v1[:min_dim]
        v2 = v2[:min_dim]
        
        # 노름 계산
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        # 0으로 나누기 방지
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        # 코사인 유사도 계산
        similarity = float(np.dot(v1, v2) / (norm1 * norm2))
        
        # 범위 제한 (수치 오차 방지)
        return max(0.0, min(1.0, similarity))
        
    except Exception as e:
        logger.error(f"유사도 계산 실패: {str(e)}")
        return 0.0

def simple_emotion(text: str) -> Optional[str]:
    """
    간단한 감정 분석
    
    Args:
        text (str): 분석할 텍스트
        
    Returns:
        Optional[str]: 감정 레이블 또는 None
    """
    try:
        if not text or not isinstance(text, str):
            return None
            
        # 텍스트 정규화
        text = text.lower().strip()
        if not text:
            return None
            
        # 감정 점수 계산
        emotion_scores = {}
        for emotion, keywords in EMOTION_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score
                
        # 가장 높은 점수의 감정 반환
        if emotion_scores:
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            return max_emotion[0]
            
        return None
        
    except Exception as e:
        logger.error(f"감정 분석 실패: {str(e)}")
        return None

def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    키워드 추출 (간단한 버전)
    
    Args:
        text (str): 텍스트
        max_keywords (int): 최대 키워드 수
        
    Returns:
        List[str]: 추출된 키워드 목록
    """
    try:
        if not text or not isinstance(text, str):
            return []
            
        # 한글 단어 추출 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', text)
        
        # 영어 단어 추출 (3글자 이상)
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        
        # 숫자 추출
        numbers = re.findall(r'\d+', text)
        
        # 모든 키워드 결합
        all_keywords = korean_words + english_words + numbers
        
        # 빈도수 기반 정렬 (간단한 버전)
        keyword_count = {}
        for keyword in all_keywords:
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            
        # 빈도수 순으로 정렬하여 상위 키워드 반환
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, count in sorted_keywords[:max_keywords]]
        
    except Exception as e:
        logger.error(f"키워드 추출 실패: {str(e)}")
        return []

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    두 텍스트 간의 유사도 계산
    
    Args:
        text1 (str): 첫 번째 텍스트
        text2 (str): 두 번째 텍스트
        
    Returns:
        float: 유사도 점수 (0-1 범위)
    """
    try:
        if not text1 or not text2:
            return 0.0
            
        # 임베딩 생성
        emb1 = simple_embed(text1)
        emb2 = simple_embed(text2)
        
        # 코사인 유사도 계산
        return cosine_similarity(emb1, emb2)
        
    except Exception as e:
        logger.error(f"텍스트 유사도 계산 실패: {str(e)}")
        return 0.0

def normalize_text(text: str) -> str:
    """
    텍스트 정규화
    
    Args:
        text (str): 원본 텍스트
        
    Returns:
        str: 정규화된 텍스트
    """
    try:
        if not text:
            return ""
            
        # 공백 정리
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 특수문자 일부 제거 (기본적인 것만)
        text = re.sub(r'[^\w\s가-힣]', '', text)
        
        return text
        
    except Exception as e:
        logger.error(f"텍스트 정규화 실패: {str(e)}")
        return text if text else ""

def get_text_features(text: str) -> Dict[str, Any]:
    """
    텍스트 특징 추출
    
    Args:
        text (str): 분석할 텍스트
        
    Returns:
        Dict[str, Any]: 텍스트 특징 딕셔너리
    """
    try:
        if not text:
            return {}
            
        features = {
            "length": len(text),
            "word_count": len(text.split()),
            "char_count": len(text.replace(" ", "")),
            "emotion": simple_emotion(text),
            "keywords": extract_keywords(text),
            "embedding": simple_embed(text)
        }
        
        return features
        
    except Exception as e:
        logger.error(f"텍스트 특징 추출 실패: {str(e)}")
        return {}

# 테스트 함수
def test_utils():
    """유틸리티 함수 테스트"""
    test_text = "나는 오늘 정말 기쁘고 행복하다"
    
    print("=== utils_lightweight 테스트 ===")
    print(f"원본 텍스트: {test_text}")
    
    # 임베딩 테스트
    embedding = simple_embed(test_text)
    print(f"임베딩 차원: {len(embedding)}")
    print(f"임베딩 샘플: {embedding[:5]}")
    
    # 감정 분석 테스트
    emotion = simple_emotion(test_text)
    print(f"감정: {emotion}")
    
    # 키워드 추출 테스트
    keywords = extract_keywords(test_text)
    print(f"키워드: {keywords}")
    
    # 유사도 테스트
    text2 = "오늘은 슬프고 우울하다"
    similarity = calculate_text_similarity(test_text, text2)
    print(f"유사도: {similarity:.3f}")
    
    # 특징 추출 테스트
    features = get_text_features(test_text)
    print(f"특징: {list(features.keys())}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_utils() 