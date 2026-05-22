// 일단 DOM이 로딩 된 다음에...
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('user-input');
    const formInput = document.getElementById('user-input-form');
    const resultDiv = document.getElementById('result');
    const chatContainer = document.getElementById('chat-container');

    // 폼 제출 이벤트 리스너
    formInput.addEventListener('submit', async (ev) => {
        ev.preventDefault();

        const chatMessage = chatInput.value.trim();
        if (!chatMessage) return; // 빈 메시지는 전송 안 함

        // 1. 내가 보낸 메시지를 먼저 화면(우측)에 추가
        appendMessage('user', chatMessage);
        chatInput.value = ''; // 입력창 비우기

        try {
            // 2. 백엔드 API에 메시지 전송 (기능 분리)
            const replyText = await fetchChatbotReply(chatMessage);
            
            // 3. 챗봇의 답변을 화면(좌측)에 추가
            appendMessage('bot', replyText);
        } catch (error) {
            console.error('에러 발생:', error);
            appendMessage('bot', '죄송해요, 서버와 연결이 원활하지 않아요. 😢');
        }
    });

    /**
     * API 통신을 담당하는 함수 (Fetch 분리)
     */
    async function fetchChatbotReply(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ chatMessage: message })
        });

        if (!response.ok) {
            throw new Error('네트워크 응답에 문제가 있습니다.');
        }

        const data = await response.json();
        return data.reply;
    }

    /**
     * 화면에 말풍선 DOM을 그리는 함수 (그리기 분리)
     * @param {string} sender - 'user' 또는 'bot'
     * @param {string} text - 메시지 내용
     */
    function appendMessage(sender, text) {
        // <div class="message user"> 또는 <div class="message bot"> 생성
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);

        // <div class="bubble">내용</div> 생성
        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('bubble');
        bubbleDiv.innerText = text;

        // 구조 조립 후 resultDiv에 삽입
        messageDiv.appendChild(bubbleDiv);
        resultDiv.appendChild(messageDiv);

        // 메시지가 쌓였을 때 자동으로 스크롤을 맨 아래로 내려줌
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
