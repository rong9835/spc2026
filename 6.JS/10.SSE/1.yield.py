
# 우리가 하곳 싶은것: 서버에서 바뀌는 데이터를 알아서 반환한다.
# 아래처럼 함수를 부르면 1을 줬다가.. 2가 됐으면 2를 주고.. 3이면 3을 주고..

# def test():
#     return 1
#     return 2
#     return 3

# x = test()
# print(x)

def test():
    yield 1
    yield 2
    yield 3

x = test()   # generator 라는것이 만들어짐 - 동적으로 바뀌는 데이터를 전달하는 객체

# print(x)
print(next(x))
print(next(x))
print(next(x))



