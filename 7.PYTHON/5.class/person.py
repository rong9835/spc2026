class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        print(f"안녕하세요, 저는 {self.name} 입니다.")

    def study(self, subject):
        print(f"{self.name} 는 {subject} 를 공부하고 있습니다.")

person1 = Person("Alice", 25)
person2 = Person("Bob", 27)

person1.greet()
person2.greet()

person1.study("Python")
person2.study("영어")

