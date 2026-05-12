class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_name(self):
        return self.name
    
    def get_age(self):
        return self.age

    def set_age(self, value):
        self.age = value
    
    def greet(self):
        print(f"안녕하세요, 저는 {self.age}살 {self.name} 입니다.")
