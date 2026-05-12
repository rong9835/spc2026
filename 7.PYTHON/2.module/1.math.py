import math

print(math.pi)
print(math.e)
print(math.sqrt(16))
print(math.sin(0)) # degree x, radian
print(math.sin(math.pi))

import datetime as dt

print(dt.datetime.now())
print(dt.datetime.now().strftime('%Y-%m-%d'))
print(dt.datetime.now().strftime('%H:%M:%S'))

a_day = dt.datetime(2025, 1, 1, 10, 00, 0)
b_day = dt.datetime(2025, 1, 1)
print(a_day)
print(b_day)


import random

print(random.random())
print(math.floor(random.random() * 100)) # 0 <= x < 100
print(random.randint(1, 100)) # 1 <= x <= 100

# 주사위 던지기
def roll_dice():
    my_number = random.randint(1, 6)
    return my_number

print("내 주사위의 숫자는: ", roll_dice())
print("내 주사위의 숫자는: ", roll_dice())
print("내 주사위의 숫자는: ", roll_dice())
print("내 주사위의 숫자는: ", roll_dice())
print("내 주사위의 숫자는: ", roll_dice())
print("내 주사위의 숫자는: ", roll_dice())

fruits = ['apple', 'banana', 'cherry', 'grape', 'orange', 'pineapple']

def pick_fruit():
    """ 앞에서 배운 randint 로 리스트에서 랜덤 과일을 반납하도록 직접 구현 """
    my_number = random.randint(0, len(fruits) - 1)
    my_pick = fruits[my_number]
    return my_pick

def pick_fruit2():
    """ 모듈안의 함수로 편하게 구현하기 """
    return random.choice(fruits)

print("내 과일은: ", pick_fruit())
print("내 과일은: ", pick_fruit())
print("내 과일은: ", pick_fruit())
print("내 과일은: ", pick_fruit())
print("내 과일은: ", pick_fruit())

print("내 과일은2: ", pick_fruit2())
print("내 과일은2: ", pick_fruit2())
print("내 과일은2: ", pick_fruit2())
print("내 과일은2: ", pick_fruit2())
print("내 과일은2: ", pick_fruit2())