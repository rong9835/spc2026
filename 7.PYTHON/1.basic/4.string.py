# 문자열을 변수에 할당하면 string 타입이 됨
s = "Hello, World"

print(s)
print(s.lower())
print(s.upper())
print(s.capitalize()) # 각 문장의 시작은 대문자
print(s.title()) # 각 단어의 시작은 대문자

s = "   Hello,    World   "
print(s.strip()) # 앞뒤 불필요한 공백제거
print(s.strip() + "!!") # 앞뒤 불필요한 공백제거
print(s.lstrip() + "!!") # 왼쪽 불필요한 공백제거
print(s.rstrip() + "!!") # 오른쪽 불필요한 공백제거

print(s.split()) # 문자열로 분할(자르기)

s = "apple banana cherry"
print(s.split())
s = "apple, banana, cherry"
print(s.split())
s = "apple,banana,cherry"  # csv = comma seperated value
print(s.split())
print(s.split(","))

s_list = s.split(",")
print(s_list)  # 리스트를 담은 자료구조
print(",".join(s_list))  #  "," 콤마로 합쳐라.. 무엇을? 나의 리스트를..
print(".".join(s_list))
print(" ".join(s_list))

s = "Hello, World"
print(s)
print(s.startswith("Hello"))  # True
print(s.startswith("hello"))  # False
print(s.endswith("World"))  # True
print(s.find("World"))  # 해당 문자가 있는 위치 (7)
print(s.find("world"))  # 해당 문자가 있는 위치 (-1) 없다

s = "김길동"
print(s.startswith("김"))  # True
print(s.startswith("홍"))  # False
