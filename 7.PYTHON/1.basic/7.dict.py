# 딕셔너리
# 키:벨류로 쌍을 이루고 있는 자료구조
my_dict = {"name": "Alice", "age": 25, "location": "서울"}
print(my_dict)

# JSON 과 비슷하게 생겨서, 웹서비스 만들때 많이 사용함. 그렇다고 JSON은 아님.
print(my_dict["name"]) # Alice 가 출력됨
print(my_dict["age"]) # 25

my_dict["car"] = "BMW"
print(my_dict)

del my_dict["location"]  # 이렇게 지울수 있는데.. del 키워드를 사용한거라 문법이 이상함.
print(my_dict)

my_age = my_dict.pop("age") # 이걸 익혀두는게 더 편함. pop 은 해당 값을 반환도 하지만, 지우기도 함.
print(my_dict)
print(my_age)

my_dict.clear() # 모든 멤버 다 지우기
print(my_dict)

# dict의 기본은 key: value 쌍의 저장
my_squares = {x: x**2 for x in range(10)}
print(my_squares)

print(my_squares.keys())
print(my_squares.values())