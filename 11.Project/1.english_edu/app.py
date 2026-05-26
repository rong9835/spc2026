# 1. openai 관련 라이브러리를 다 불러온다 (dotenv, openai 등등)
# 2. OOO 페이지 (우리의 최종 페이지) 에서 채팅창 FE 를 만든다.
# 3-1. 그 FORM의 입력값을 BE에서 POST로 받아서, chatgpt API 호출한다. (그냥 아무말이나 해도 됨.)
# 3-2. 응답 받아서 다시 프런트엔드에 반환해서 결과 출력한다.
# 3-3. [추가] 복습을 원하면 SSE 기반에 스트리밍 구현해봐도 됨
# 4. 그럼 이제, 진짜 우리의 이 상황 (학년, 커리큐럼) 에 대해서 영어로 대화를 하도록 만든다.
# 5. [추가] 메모리를 통해서 대화 내용 컨텍스트를 기억하게 한다.


from flask import Flask, render_template

app = Flask(__name__)

# 각 학년별 커리큐럼 데이터 - dict 자료 구조의 key-value
curriculums = {
    # key: [value]
    1: ['기초 인사', '간단한 문장', '동물이름'],
    2: ['학교 생활', '가족 소개', '자기 소개'],
    3: ['취미와 운동', '날씨 묘사', '간단한 이야기'],
    4: ['쇼핑과 가격', '음식 주문', '여행 이야기'],
    5: ['역사와 문화', '과학과 자연', '사회 이슈'],
    6: ['미래 계획', '진로 탐색', '세계 여행'],
}


@app.route('/')
def home():
    return render_template('home.html', grades=curriculums.keys())


@app.route('/grade/<int:grade>')
def grade(grade):
    if grade in curriculums:
        curriculums_index = list(enumerate(curriculums[grade]))

        return render_template(
            'grade.html',
            grade=grade,
            grades=curriculums.keys(),
            curriculums=curriculums_index,
        )
    return '해당학년은 존재하지 않습니다', 404


@app.route('/grade/<int:grade>/curriculum/<int:curriculum_id>')
def curriculum(grade, curriculum_id):
    if grade in curriculums and 0 <= curriculum_id < len(curriculums[grade]):
        curriculum_title = curriculums[grade][curriculum_id]
        return render_template(
            'curriculum.html',
            grade=grade,
            grades=curriculums.keys(),
            curriculum_title=curriculum_title,
        )
    return '해당 커리큘럼은 존재하지 않습니다', 404


if __name__ == '__main__':
    app.run(debug=True)
