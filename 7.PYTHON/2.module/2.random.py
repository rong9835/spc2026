import random
import string

# alphabet = ['a', 'b', 'c', ..., 'A', 'B', ... '1', '2', ...]

def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

print(generate_random_password())
print(generate_random_password(16))
print(generate_random_password(32))

