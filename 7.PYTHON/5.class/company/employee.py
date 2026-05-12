from person import Person

class Employee(Person):
    def __init__(self, name, age, company):
        super().__init__(name, age)
        self.company = company

    def greet(self): # 메서드 오버라이딩
        print(f"안녕하세요, 저는 {self.company} 에 다니고 있는 {self.name} 입니다.")

