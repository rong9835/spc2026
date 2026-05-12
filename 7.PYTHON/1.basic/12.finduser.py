users = [
    {"name": "김민준", "age": 25, "location": "서울", "car": "아반떼"},
    {"name": "이서연", "age": 31, "location": "부산", "car": "소나타"},
    {"name": "박지훈", "age": 28, "location": "대전", "car": "테슬라 모델3"},
    {"name": "최유진", "age": 22, "location": "인천", "car": "레이"},
    {"name": "정도현", "age": 35, "location": "광주", "car": "그랜저"},
    {"name": "한지민", "age": 27, "location": "대구", "car": "셀토스"},
    {"name": "윤태호", "age": 41, "location": "울산", "car": "BMW X5"},
    {"name": "김수아", "age": 25, "location": "수원", "car": "캐스퍼"},
    {"name": "오세훈", "age": 38, "location": "제주", "car": "쏘렌토"},
    {"name": "백예린", "age": 29, "location": "청주", "car": "아이오닉5"}
]

def find_user_and_print(name):
    for user in users:
        # if user["name"] == name:  # 정확한 매칭 찾기
        if user["name"].startswith(name):    # 앞글자 즉 성씨로 찾기
            print(user)

find_user_and_print("김")
find_user_and_print("오")

print('-'*30)

def find_user_and_return(name):
    found = []  # 찾은 사용자를 담을 바구니 (리스트 변수)

    for user in users:
        if user["name"].startswith(name):
            found.append(user)
    
    return found

# found_users = find_user_and_return("김")
# found_users = find_user_and_return("오")
found_users = find_user_and_return("구")
print("찾은 사용자:", found_users)

print('-'*30)
def find_users2(name=None, age=None):
    """이름 또는 나이를 입력받아 매칭되는 사람을 반환한다"""
    found = []

    for user in users:
        if name is not None and age is not None:
            if user["name"] == name and user["age"] == age:
                found.append(user)
        elif name is not None:
            if user["name"] == name:
                found.append(user)
        elif age is not None:
            if user["age"] == age:
                found.append(user)

    return found

# print(find_users2("김민준"))
# print(find_users2("김민준", 24))
# print(find_users2("김민준", 25))
print(find_users2(age=25)) # ??? 나이로만 찾으려면 어떻게 ???

print("-"*30)
def find_users2_better(name=None, age=None, location=None):
    """이름 또는 나이를 입력받아 매칭되는 사람을 반환한다"""
    found = []
    for user in users:
        #      true      or    비교문
        if (name is None or user["name"] == name) and (age is None or user["age"] == age) and (location is None or user["location"] == location):
            found.append(user)
    return found

# print(find_users2_better("김민준"))
# print(find_users2_better("김민준", 24))
print(find_users2_better("김민준", 25, "서울"))
# print(find_users2_better(age=25))

print('-'*30)

search_condition1 = {
    "name": "김민준"
}

search_condition2 = {
    "name": "김민준",
    "age": 25
}

search_condition3 = {
    "age": 25
}

search_condition3 = {
    "min_age": 25
}

# def find_users2_best(condition):
#     found = []
#     for user in users:
#         if user.get("name") == condition.get("name", "") and \
#             user.get("age") >= condition.get("min_age", 0) and \
#             user.get("location") == condition.get("location", ""):
#             found.append(user)

#     return found

# print(find_users2_best(search_condition1))
