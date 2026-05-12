def add_numbers(a, b):
    """이 함수는 이자를 두개 받아서 합을 반환하는 함수입니다."""
    result = a + b
    return result

sum = add_numbers(3, 4)
print(f"두 수의 합은 {sum} 입니다.")

def add_numbers2(a, b):
    return a, b, a+b

input1, input2, sum = add_numbers2(3, 4)
print(f"인자1은 {input1}, 인자2는 {input2}, 두 수의 합은 {sum} 입니다.")

def calculate_all(a, b):
    """ 이 함수는 두 수의 입력을 받아 4칙연산된 결과를 모두 반환합니다."""
    addition = a + b
    subtraction = a - b
    multiplication = a * b
    division = a / b

    return addition, subtraction, multiplication, division

add, sub, mul, div = calculate_all(3, 4)
print(f"덧셈은 {add}, 뺄셈은 {sub}, 곱셈은 {mul}, 나눗셈은 {div}")

add, _, mul, _ = calculate_all(5, 6)
print(f"덧셈은 {add}, 곱셈은 {mul} 입니다.")

print('-'*30)

def create_profile(name, age, city="서울", job="학생"):
    profile = f"이름: {name}, 나이: {age}, 지역: {city}, 직업: {job}"
    return profile

print(create_profile('홍길동', 23))
print(create_profile('김길동', 25))
print(create_profile('박길동', 27))
print(create_profile('이길동', 27, "부산"))
print(create_profile('최길동', 27, "부산", "직장인"))
