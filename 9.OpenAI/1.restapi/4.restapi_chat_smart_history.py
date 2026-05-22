from dotenv import load_dotenv
import os
import requests

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# -----------------------------
# 기본 설정
# -----------------------------
SYSTEM_PROMPT = '너는 나를 잘 도와주는 경력 20년차의 작명가야.'

message = [
    {'role': 'system', 'content': SYSTEM_PROMPT}
]

MAX_RECENT_MESSAGES = 10   # 최근 대화 유지 개수


# -----------------------------
# OpenAI API 호출 함수
# -----------------------------
def call_chatgpt(messages, temperature=1.0):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json={
            'model': 'gpt-3.5-turbo',
            'messages': messages,
            'temperature': temperature,
        },
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
    )

    response.raise_for_status()

    data = response.json()
    return data['choices'][0]['message']['content']


# -----------------------------
# 대화 요약 함수
# -----------------------------
def summarize_conversation(conversation_list):
    """
    오래된 대화 내용을 요약한다.
    """

    summary_prompt = [
        {
            'role': 'system',
            'content': (
                '너는 대화 요약 전문가야. '
                '사용자와 AI의 대화를 핵심만 간결하게 요약해줘. '
                '중요한 요청사항, 취향, 맥락을 유지해.'
            )
        },
        {
            'role': 'user',
            'content': str(conversation_list)
        }
    ]

    summary = call_chatgpt(summary_prompt, temperature=0.3)

    return summary


# -----------------------------
# 메시지 관리 함수
# -----------------------------
def manage_message_history():
    """
    대화가 길어지면 오래된 내용을 요약해서
    message[1] 에 저장한다.
    """

    global message

    # system 제외 실제 대화 수 계산
    actual_conversation_count = len(message) - 1

    if actual_conversation_count > MAX_RECENT_MESSAGES:

        # 기존 summary 있는지 확인
        has_summary = (
            len(message) > 1 and
            message[1]['role'] == 'system' and
            '[대화 요약]' in message[1]['content']
        )

        # 최근 메시지 제외한 오래된 대화 추출
        old_messages = message[1:-MAX_RECENT_MESSAGES]

        # 이전 summary 도 함께 포함
        if has_summary:
            old_messages.insert(0, message[1])

        # 요약 생성
        summary_text = summarize_conversation(old_messages)

        summary_message = {
            'role': 'system',
            'content': f'[대화 요약]\n{summary_text}'
        }

        # 새 메시지 구성
        recent_messages = message[-MAX_RECENT_MESSAGES:]

        message = [
            message[0],        # 원래 시스템 프롬프트
            summary_message    # 요약
        ] + recent_messages


# -----------------------------
# 챗봇 함수
# -----------------------------
def ask_chatbot(user_input):
    global message

    message.append({
        'role': 'user',
        'content': user_input
    })

    try:
        final_response = call_chatgpt(message)

        message.append({
            'role': 'assistant',
            'content': final_response
        })

        # 대화 기록 관리
        manage_message_history()

        return final_response

    except Exception as e:
        return f'오류 발생: {e}'


# -----------------------------
# 메인 루프
# -----------------------------
while True:

    user_input = input('\n당신의 질문: ').strip()

    if user_input.lower() in ['quit', 'exit', '종료', '끝']:
        print('대화를 종료합니다. 안녕히 가세요.')
        break

    print('대화를 생성중입니다. 잠시만 기다려 주세요....')

    response = ask_chatbot(user_input)

    print('챗봇 응답:', response)
    print('-' * 60)
    