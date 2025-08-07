# 세션 저장 및 불러오기 시스템 수정

## 문제점
- 새로고침 시 대화 내역이 사라짐
- 세션 목록이 표시되지 않음
- 이전 대화를 불러올 수 없음

## 원인
`chat.html`에서 사용하는 다음 API들이 `app.py`에 구현되어 있지 않았습니다:
1. `GET /api/sessions` - 세션 목록 가져오기
2. `GET /api/sessions/{session_id}/messages` - 특정 세션의 메시지들 가져오기

## 해결 방법

### 1. ✅ API 엔드포인트 추가 (app.py 2080-2224줄)

#### GET /api/sessions
- 사용자의 세션 목록을 MongoDB 또는 메모리 캐시에서 조회
- 각 세션의 ID, 이름, 생성일, 마지막 메시지 시간, 메시지 수 반환
- 최근 50개 세션만 반환 (성능 최적화)

#### GET /api/sessions/{session_id}/messages
- 특정 세션의 모든 메시지를 시간순으로 조회
- "사용자: xxx\nAI: yyy" 형식을 개별 메시지로 분리하여 반환
- role(user/assistant), content, timestamp 포함

### 2. 데이터 저장 구조
현재 대화는 `save_to_aura_memory` 함수를 통해 저장됩니다:
- MongoDB 사용 가능 시: `aura_collection`에 저장
- MongoDB 없을 시: 메모리 캐시 `memory_cache["aura_memories"]`에 저장

### 3. 세션 ID 관리
- 세션 ID는 `generate_session_id()` 함수로 생성
- 형식: `session_타임스탬프_랜덤문자열`
- chat.html에서 localStorage에 현재 세션 ID 저장

## 테스트 방법

1. **새 대화 시작**
   - 채팅 페이지 접속
   - 메시지 전송
   - 페이지 새로고침
   - 대화 내역이 유지되는지 확인

2. **세션 목록 확인**
   - 왼쪽 사이드바에 세션 목록 표시 확인
   - 여러 세션 생성 후 목록에 나타나는지 확인

3. **이전 대화 불러오기**
   - 세션 목록에서 이전 대화 클릭
   - 해당 세션의 대화 내역이 로드되는지 확인

## 주의사항

- MongoDB가 없는 환경에서는 메모리 캐시를 사용하므로 서버 재시작 시 데이터가 사라집니다
- 세션 ID가 "undefined", "null", 빈 문자열인 경우는 필터링됩니다
- 각 사용자는 자신의 세션만 볼 수 있습니다 (user_id 기반 필터링)

## 추가 개선 사항 (선택사항)

1. **세션 이름 편집 기능**
   - 현재는 "대화 session_xxx..." 형식
   - 사용자가 원하는 이름으로 변경 가능하도록 개선

2. **세션 삭제 기능**
   - 현재 UI에는 있지만 백엔드 API 필요
   - `DELETE /api/sessions/{session_id}` 엔드포인트 추가

3. **세션 검색 기능**
   - 많은 세션이 있을 때 특정 대화 찾기
   - 키워드 기반 검색 기능 추가

4. **파일 기반 백업**
   - MongoDB 없을 때도 영구 저장을 위해
   - JSON 파일로 세션 데이터 저장/로드 