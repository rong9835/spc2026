numbers = [1, 2, 3, 4, 5]

# for num in [1, 2, 3, 4, 5]:
# for num in range(1, 6):
for num in numbers:
    if num % 2 == 0:
        print(f"숫자 {num} 은 짝수 입니다.")
    else:
        print(f"숫자 {num} 은 홀수 입니다.")


even_numbers = []
odd_numbers = []

for num in numbers:
    if num % 2 == 0:
        even_numbers.append(num)
    else:
        odd_numbers.append(num)

print(f"짝수: {even_numbers}")
print(f"홀수: {odd_numbers}")

import time

n = 100
count = 0

start_time = time.time()   # 현재 시간 저장

# 코드의 효율성... 시간복잡도 O(n^4) /공간복잡도
for i in range(n):
    for j in range(n):
        for k in range(n):
            for l in range(n):
                count += 1

end_time = time.time()

exec_time = end_time - start_time

print("합산: ", count)
print(f"총 소요시간은: {exec_time:.1f} 초가 소요되었습니다.")
