import os

print(os.getcwd())
# print(os.mkdir("Hello"))
# print(os.rmdir("Hello"))

os.chdir("C:/src/SPC2025")
cwd = os.getcwd()

print(cwd)
print(os.listdir(cwd))
