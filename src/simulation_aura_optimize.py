"""
simulation_aura_optimize.py

독립 실행 가능 최적화 스크립트
- 다수 시나리오에 대해 반복 테스트 실행
- eora_dynamic_params.KEYWORD_PARAMS와 DEFAULT_PARAMS 기반으로 temperature 및 top_p 평균 계산
- 시나리오별 최적 평균 파라미터 제안 파일(suggested_params.json) 생성
"""

import os
import json
import statistics
from EORA.eora_dynamic_params import KEYWORD_PARAMS, DEFAULT_PARAMS, decide_chat_params

# 테스트 시나리오 (예: 50가지)
scenarios = [
    "안녕, 오늘 날씨가 궁금해",
    "새로운 모바일 앱 기획 아이디어가 필요해",
    "파이썬으로 데이터 분석하는 방법 알려줘",
    "디버깅 중인 코드에서 IndexError를 해결해줘",
    "마케팅 캠페인 전략을 제안해줘",
    "CI/CD 파이프라인 구축하기",
    "머신러닝 모델의 과적합 문제를 해결하려면?",
    "보안 취약점 스캔 도구 추천",
    "UX 디자인 팁을 알려줘",
    "프로젝트 관리 도구 비교",
    "SQL 데이터베이스 성능 튜닝",
    "REST API 설계 모범 사례",
    "팀 빌딩 워크숍 아이디어",
    "재무 계획 모델링",
    "글쓰기 스타일 교정",
    "소설 플롯 아이디어 제안",
    "심리 상담 대화 예시",
    "시간 관리 팁을 알려줘",
    "네트워크 장애 대응 시나리오",
    "요리 레시피 추천",
    "헬스케어 앱의 주요 기능",
    "Frontend와 Backend 통합 전략",
    "AWS 비용 최적화 방법",
    "DevOps 자동화 스크립트 예제",
    "데이터 시각화 라이브러리 비교",
    "번역 모델 활용 사례",
    "면접 질문 연습",
    "법률 자문 예시 (비전문)",
    "고객 지원 챗봇 스크립트",
    "재난 대응 프로토콜",
    "여행 일정 짜기",
    "건강 관리 루틴 설계",
    "음악 작곡 아이디어",
    "시 쓰기 주제 제안",
    "학교 과제 도움",
    "코드 리팩토링 전략",
    "간단 레시피 추천",
    "스포츠 경기 일정 분석",
    "영화 추천",
    "금융 시장 동향 요약",
    "심리 테스트 설계",
    "교육 커리큘럼 기획",
    "신제품 출시 발표문",
    "스토리보드 작성",
    "IoT 디바이스 제어 시나리오",
    "게임 디자인 문서 예시",
    "AI 윤리 가이드라인",
    "소셜 미디어 콘텐츠 캘린더"
]

# 반복 횟수
iterations = 10

# 결과 수집 구조 초기화
# 키: 키워드 or 'DEFAULT', 값: 리스트 of (temp, top_p)
results = {kw: [] for kw in KEYWORD_PARAMS}
results['DEFAULT'] = []

# 시뮬레이션 반복 실행
for i in range(iterations):
    for scenario in scenarios:
        messages = [{"role": "user", "content": scenario}]
        params = decide_chat_params(messages)
        # 시나리오에 매칭된 키워드 결정
        bucket = 'DEFAULT'
        for kw in KEYWORD_PARAMS:
            if kw in scenario:
                bucket = kw
                break
        results[bucket].append((params['temperature'], params['top_p']))

# 최적 파라미터 제안 계산
suggestions = {}
for bucket, vals in results.items():
    if not vals:
        continue
    temps = [v[0] for v in vals]
    tops = [v[1] for v in vals]
    suggestions[bucket] = {
        "temperature": round(statistics.mean(temps), 2),
        "top_p": round(statistics.mean(tops), 2)
    }

# 제안된 파라미터 JSON 출력
output_file = os.path.join(os.path.dirname(__file__), "suggested_params.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(suggestions, f, ensure_ascii=False, indent=2)

print("최적화 제안 생성 완료:", output_file)
print(json.dumps(suggestions, ensure_ascii=False, indent=2))
