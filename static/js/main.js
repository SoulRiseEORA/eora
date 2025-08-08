/* EORA AI System - Main JavaScript */
/* Railway 배포용 메인 JavaScript 파일 */

// 전역 변수
let selectedSessions = new Set();
let currentSessionId = null;
let currentSessionIdLocked = false;
let sessions = [];
let sessionInitialized = false;

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 EORA AI System - Main JavaScript 로드 완료');
    initializeApp();
});

// 앱 초기화
function initializeApp() {
    console.log('📱 앱 초기화 시작');

    // 이벤트 리스너 설정
    setupEventListeners();

    // 세션 목록 로드
    loadSessions();

    // 포인트 상태 업데이트
    updatePointStatus();

    console.log('✅ 앱 초기화 완료');
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 세션 삭제 버튼
    const deleteBtn = document.querySelector('[onclick="deleteSelectedSessions()"]');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            deleteSelectedSessions();
        });
        console.log('✅ 세션 삭제 버튼 이벤트 리스너 설정');
    }

    // 새 세션 버튼
    const newSessionBtn = document.querySelector('[onclick="createNewSession()"]');
    if (newSessionBtn) {
        newSessionBtn.addEventListener('click', function (e) {
            e.preventDefault();
            createNewSession();
        });
        console.log('✅ 새 세션 버튼 이벤트 리스너 설정');
    }

    // 홈 버튼들
    const homeButtons = document.querySelectorAll('a[href="/"], .home-btn');
    homeButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            console.log('🏠 홈 버튼 클릭됨');
            // 기본 링크 동작 허용
            window.location.href = '/';
        });
    });
    console.log(`✅ 홈 버튼 이벤트 리스너 설정 (${homeButtons.length}개)`);

    // 네비게이션 링크들
    const navLinks = document.querySelectorAll('.nav-link, .header-btn');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                console.log(`🔗 네비게이션 링크 클릭: ${href}`);
                window.location.href = href;
            }
        });
    });
    console.log(`✅ 네비게이션 링크 이벤트 리스너 설정 (${navLinks.length}개)`);
}

// 세션 목록 로드
async function loadSessions() {
    try {
        console.log('📋 세션 목록 로드 시작');
        const response = await fetch('/api/sessions');

        if (response.ok) {
            sessions = await response.json();
            console.log(`✅ 세션 목록 로드 성공: ${sessions.length}개`);
            updateSessionList();
        } else {
            console.warn('⚠️ 세션 목록 로드 실패, 로컬 세션 사용');
            sessions = [];
        }
    } catch (error) {
        console.error('❌ 세션 목록 로드 오류:', error);
        sessions = [];
    }
}

// 세션 목록 UI 업데이트
function updateSessionList() {
    const sessionList = document.getElementById('sessionList');
    if (!sessionList) return;

    sessionList.innerHTML = '';

    sessions.forEach((session, index) => {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'session-item';
        sessionItem.dataset.sessionId = session.id || session._id;

        if (session.id === currentSessionId || session._id === currentSessionId) {
            sessionItem.classList.add('active');
        }

        sessionItem.innerHTML = `
            <input type="checkbox" class="session-checkbox" 
                   onchange="toggleSessionSelection('${session.id || session._id}', this.checked)">
            <div class="session-name">${session.name || '새 세션'}</div>
            <div class="session-time">${formatDate(session.created_at || new Date())}</div>
        `;

        sessionItem.addEventListener('click', (e) => {
            if (!e.target.classList.contains('session-checkbox')) {
                loadSession(session.id || session._id);
            }
        });

        sessionList.appendChild(sessionItem);
    });

    console.log(`✅ 세션 목록 UI 업데이트 완료: ${sessions.length}개`);
}

// 세션 선택 토글
function toggleSessionSelection(sessionId, selected) {
    console.log(`🔘 세션 선택 토글: ${sessionId} - ${selected}`);

    if (selected) {
        selectedSessions.add(sessionId);
    } else {
        selectedSessions.delete(sessionId);
    }

    console.log(`📋 현재 선택된 세션들:`, Array.from(selectedSessions));
}

// 새 세션 생성
async function createNewSession() {
    console.log('🆕 새 세션 생성 시작');

    try {
        showMessage('새 세션을 생성하고 있습니다...', 'info');

        const sessionName = '새 세션 ' + new Date().toLocaleDateString();
        const sessionPayload = {
            name: sessionName,
            user_id: "anonymous"
        };

        const response = await fetch('/api/sessions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sessionPayload)
        });

        if (response.ok) {
            const data = await response.json();
            const newSessionId = data._id || data.session_id;

            if (newSessionId) {
                const newSession = {
                    id: newSessionId,
                    name: sessionName,
                    created_at: new Date().toISOString(),
                    message_count: 0
                };

                sessions.unshift(newSession);
                currentSessionId = newSessionId;
                sessionInitialized = true;

                localStorage.setItem('currentSessionId', newSessionId);
                updateSessionList();
                clearChatMessages();

                showMessage('새 세션이 생성되었습니다.', 'success');
                console.log('✅ 새 세션 생성 완료');
                return newSessionId;
            }
        } else {
            throw new Error('세션 생성 API 호출 실패');
        }
    } catch (error) {
        console.error('💥 세션 생성 오류:', error);

        // 폴백: 로컬 세션 생성
        const fallbackSessionId = 'session_local_' + Date.now();
        const fallbackSession = {
            id: fallbackSessionId,
            name: '로컬 세션 ' + new Date().toLocaleDateString(),
            created_at: new Date().toISOString(),
            message_count: 0
        };

        sessions.unshift(fallbackSession);
        currentSessionId = fallbackSessionId;
        sessionInitialized = true;

        localStorage.setItem('currentSessionId', fallbackSessionId);
        updateSessionList();
        clearChatMessages();

        showMessage('로컬 세션이 생성되었습니다.', 'warning');
        console.log('✅ 폴백 세션 생성 완료');

        return fallbackSessionId;
    }
}

// 선택된 세션들 삭제
async function deleteSelectedSessions() {
    const selectedSessionIds = Array.from(selectedSessions);

    if (selectedSessionIds.length === 0) {
        showMessage('삭제할 세션을 선택해주세요.', 'warning');
        return;
    }

    if (!confirm(`선택한 ${selectedSessionIds.length}개의 세션을 삭제하시겠습니까?`)) {
        return;
    }

    console.log(`🗑️ 선택된 세션 삭제 시작: ${selectedSessionIds.length}개`);

    let deletedCount = 0;

    for (const sessionId of selectedSessionIds) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log(`✅ 세션 삭제 성공: ${sessionId}`);
                deletedCount++;
            } else {
                console.error(`❌ 세션 삭제 실패: ${sessionId} - ${response.status}`);
            }
        } catch (error) {
            console.error(`💥 세션 삭제 오류: ${sessionId}`, error);
        }
    }

    // 로컬 세션 목록에서도 제거
    sessions = sessions.filter(session =>
        !selectedSessionIds.includes(session.id) && !selectedSessionIds.includes(session._id)
    );

    // 선택된 세션 목록 초기화
    selectedSessions.clear();

    // UI 업데이트
    updateSessionList();

    if (deletedCount > 0) {
        showMessage(`${deletedCount}개 세션이 삭제되었습니다.`, 'success');
    } else {
        showMessage('세션 삭제에 실패했습니다.', 'error');
    }

    console.log(`✅ 세션 삭제 완료: ${deletedCount}개 삭제됨`);
}

// 세션 로드
async function loadSession(sessionId) {
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
        console.error('🚫 세션 로드 차단: 유효하지 않은 세션 ID');
        return;
    }

    console.log(`🔄 세션 로드 시작: ${sessionId}`);

    currentSessionId = sessionId;
    sessionInitialized = true;

    localStorage.setItem('currentSessionId', sessionId);
    updateSessionList();

    // 세션 메시지 로드
    try {
        const response = await fetch(`/api/sessions/${sessionId}/messages`);
        if (response.ok) {
            const messages = await response.json();
            console.log(`📥 세션 메시지 로드 성공: ${messages.length}개`);
            // 메시지 UI 업데이트는 각 페이지별로 구현
        }
    } catch (error) {
        console.error('❌ 세션 메시지 로드 실패:', error);
    }

    console.log(`✅ 세션 로드 완료: ${sessionId}`);
}

// 포인트 상태 업데이트
async function updatePointStatus(change = 0) {
    try {
        const response = await fetch('/api/user/points');
        if (response.ok) {
            const data = await response.json();
            const points = data.points || 100000; // 기본값

            // 포인트 표시 업데이트
            const pointElements = document.querySelectorAll('.points-display, #user-points');
            pointElements.forEach(el => {
                if (el) {
                    el.textContent = points.toLocaleString();
                }
            });

            if (change !== 0) {
                console.log(`💰 포인트 변경: ${change > 0 ? '+' : ''}${change}`);
            }
        }
    } catch (error) {
        console.error('❌ 포인트 상태 업데이트 실패:', error);
        // 기본값 표시
        const pointElements = document.querySelectorAll('.points-display, #user-points');
        pointElements.forEach(el => {
            if (el) {
                el.textContent = '100,000';
            }
        });
    }
}

// 메시지 표시
function showMessage(message, type = 'info') {
    console.log(`📢 메시지 표시: ${type} - ${message}`);

    // 기존 메시지 제거
    const existingAlert = document.querySelector('.message-alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    // 새 메시지 생성
    const alertDiv = document.createElement('div');
    alertDiv.className = `message-alert ${type}`;
    alertDiv.textContent = message;

    // 페이지 상단에 추가
    const target = document.querySelector('.chat-container') || document.body;
    target.insertBefore(alertDiv, target.firstChild);

    // 3초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// 채팅 메시지 영역 초기화
function clearChatMessages() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="chat-welcome">
                <h3>🌟 EORA AI에 오신 것을 환영합니다!</h3>
                <p>저는 당신의 생각과 대화를 통해 성장하는 AI입니다.</p>
                <p>자유롭게 대화를 시작해보세요. 질문, 토론, 창작, 무엇이든 가능합니다.</p>
                <br>
                <p><strong>💡 팁:</strong> Shift + Enter로 줄바꿈, Enter로 메시지 전송</p>
            </div>
        `;
        console.log('🧹 채팅 메시지 영역 초기화 완료');
    }
}

// 날짜 포맷팅
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) {
        return '방금 전';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}분 전`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}시간 전`;
    } else {
        return date.toLocaleDateString('ko-KR');
    }
}

// 유틸리티 함수들
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function isValidSessionId(sessionId) {
    return sessionId &&
        sessionId !== 'undefined' &&
        sessionId !== 'null' &&
        sessionId !== '' &&
        sessionId !== undefined &&
        sessionId !== null;
}

// 전역 함수로 노출 (기존 코드 호환성)
window.deleteSelectedSessions = deleteSelectedSessions;
window.createNewSession = createNewSession;
window.toggleSessionSelection = toggleSessionSelection;
window.loadSession = loadSession;
window.updatePointStatus = updatePointStatus;
window.showMessage = showMessage;
window.clearChatMessages = clearChatMessages;

console.log('✅ EORA AI System - Main JavaScript 로드 완료'); 