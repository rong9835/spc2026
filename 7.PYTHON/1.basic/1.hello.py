print('Hello, Python')
print('Hello', 'Python')
print('Hello' + 'Python')
print('Hello, ' + 'Python')
print("Hello, " + 'Python')
print('"Hello", ' + "'Python'" + "!!")
num = 5
name = "홍길동"
print("Hello, {}".format(name));
print("Hello, {}. My lucky number is {}".format(name, num));
print("Hello, {0}. My lucky number is {1}".format(name, num));
print("Hello, {1}. My lucky number is {0}".format(name, num));
print("Hello, %s" % name)
print("Hello, %s" % name, end="")
# print("홍길동", end="")
print("홍길동", end="\n")
multiline = """
여기는 멀티라인으로
긴 주석을 넣을수 있습니다.
이걸 주석이라고 배웠을텐데, 사실은 주석이 아니고 여러줄의 문자열입니다.
"""
print(multiline)