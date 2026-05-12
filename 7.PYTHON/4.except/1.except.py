
try:
    result = 10 / 0
except ZeroDivisionError:
    print('0으로 나눌 수 없습니다.')
except:
    print("알수 없는 오류입니다.")


try:
    number = int("hello")
except ValueError:
    print("해당 글자는 숫자로 변환할수 없습니다.")
except:
    print("아몰랑.. 에러 일단 통과..")


alist = [1,2,3]
try:
    alist[3]
except IndexError:
    print("입력 범위를 초과하였습니다.")

try:
    with open("없는파일명.txt", "r") as file:
        data = file.read()
except FileNotFoundError:
    print("해당 파일이 존재하지 않습니다.")
