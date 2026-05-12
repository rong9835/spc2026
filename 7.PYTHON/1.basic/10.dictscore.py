students = {
    "김민준": 87,
    "이서연": 92,
    "박지훈": 78,
    "최유진": 95,
    "정도현": 81,
    "한지민": 89,
    "윤태호": 73,
    "강수아": 98,
    "오세훈": 84,
    "백예린": 91
}

print(students)

def get_a_student(students):
    a_students = []
    for name, score in students.items(): # dict의 요소를 하나씩 가져옴 (items())
        if score >= 90:
            a_students.append(name)
    return a_students

print("A등급 학생: ", get_a_student(students))
