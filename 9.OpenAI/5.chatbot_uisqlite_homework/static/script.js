document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('user-input');
    const formInput = document.getElementById('user-input-form');
    const resultDiv = document.getElementById('result');
    const chatContainer = document.getElementById('chat-container');
    const userSetup = document.getElementById('user-setup');
    const userIdInput = document.getElementById('user-id-input');
    const startBtn = document.getElementById('start-btn');
    const sidebar = document.getElementById('sidebar');
    const sessionList = document.getElementById('session-list');
    const newChatBtn = document.getElementById('new-chat-btn');

    let sessionId = crypto.randomUUID();
    let userId = '';

    // 시작 버튼
    startBtn.addEventListener('click', () => {
        const name = userIdInput.value.trim();
        if (!name) return;

        userId = name;
        userSetup.style.display = 'none';
        sidebar.style.display = 'flex';
        chatContainer.style.display = 'block';
        formInput.style.display = 'flex';
        loadSessions();
    });

    // 새 대화 버튼
    newChatBtn.addEventListener('click', () => {
        sessionId = crypto.randomUUID();
        resultDiv.innerHTML = '';
    });

    // 세션 목록 불러오기
    async function loadSessions() {
        const response = await fetch(`/api/sessions?userId=${userId}`);
        const data = await response.json();
        renderSessionList(data.sessions);
    }

    // 세션 목록 화면에 그리기
    function renderSessionList(sessions) {
        sessionList.innerHTML = '';

        if (sessions.length === 0) {
            sessionList.innerHTML = '<p class="no-sessions">대화 내역 없음</p>';
            return;
        }

        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = 'session-item';

            const titleSpan = document.createElement('span');
            titleSpan.className = 'session-title';
            titleSpan.textContent = session.title;
            titleSpan.addEventListener('click', () => loadSession(session.sessionId));

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'session-delete-btn';
            deleteBtn.textContent = '삭제';
            deleteBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                await fetch(`/api/history?sessionId=${session.sessionId}`, { method: 'DELETE' });
                if (sessionId === session.sessionId) {
                    resultDiv.innerHTML = '';
                    sessionId = crypto.randomUUID();
                }
                loadSessions();
            });

            item.appendChild(titleSpan);
            item.appendChild(deleteBtn);
            sessionList.appendChild(item);
        });
    }

    // 특정 세션 대화 불러오기
    async function loadSession(sid) {
        sessionId = sid;
        const response = await fetch(`/api/history?sessionId=${sid}`);
        const data = await response.json();
        resultDiv.innerHTML = '';
        data.history.forEach(item => {
            appendMessage(item.role === 'user' ? 'user' : 'bot', item.content);
        });
    }

    // 폼 제출
    formInput.addEventListener('submit', async (ev) => {
        ev.preventDefault();

        const chatMessage = chatInput.value.trim();
        if (!chatMessage) return;

        appendMessage('user', chatMessage);
        chatInput.value = '';

        try {
            const replyText = await fetchChatbotReply(chatMessage);
            appendMessage('bot', replyText);
            loadSessions(); // 새 메시지 보낸 후 사이드바 갱신
        } catch (error) {
            appendMessage('bot', '죄송해요, 서버와 연결이 원활하지 않아요. 😢');
        }
    });

    async function fetchChatbotReply(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chatMessage: message, sessionId: sessionId, userId: userId })
        });
        if (!response.ok) throw new Error('네트워크 오류');
        const data = await response.json();
        return data.reply;
    }

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('bubble');
        bubbleDiv.innerText = text;
        messageDiv.appendChild(bubbleDiv);
        resultDiv.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
