def numbers():
    for i in range(1000000):
        yield i

for num in numbers():
    print(num)
    if num >= 100:
        break
