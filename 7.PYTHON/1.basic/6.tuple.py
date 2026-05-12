# 튜플 (읽기전용 리스트)
my_list = [1, 2, 3, 4, 5]
my_tuple = (1, 2, 3, 4, 5)

print(my_list)
print(my_tuple)

print(my_list[2])
print(my_tuple[2])

my_list[2] = 99
# my_tuple[2] = 99  # 튜플의 값을 쓸 수 없음

print(my_list[-1])
print(my_tuple[-1])

print(my_list[3:5])
print(my_tuple[3:5])

print(my_list[0:1])
print(my_tuple[0:1])  # (1) 이 아니고 (1,)  <-- 그냥 (1)

# 튜플을 받아 왔는데, 값을 쓰고 싶으면??
my_newlist = list(my_tuple)  # 타입 변환을 해서 복제본을 만듦
print(my_newlist)
my_newlist[2] = 88
print(my_newlist)
print(my_tuple)

my_newtuple = tuple(my_newlist)  # 쓰기가 불가능한 리스트... => 튜플
print(my_newtuple)
my_newlist[2] = 77
print(my_newtuple)

print('-'*30)
a, b, c = (1, 2, 3)  # 튜플 언패킹 () 튜플로 감싸져 있는걸 분해
print(a, b, c)

a_person = ("John", 23, "Student")
print(a_person)
name, age, occ = a_person
print(name)
print(age)