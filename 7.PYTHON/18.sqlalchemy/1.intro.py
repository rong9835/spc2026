# pip install sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///example.db')

# 객체를 정의
Base = declarative_base()

# 테이블 정의
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

# 실행
Base.metadata.create_all(engine)

# 활용
Session = sessionmaker(bind=engine)
session = Session()

new_user = User(name="홍길동", age=25)
session.add(new_user)

new_user = User(name="고길동", age=35)
session.add(new_user)

session.commit()

print('-' * 30)
users = session.query(User).all()
for user in users:
    print(user.name, user.age)
print('-' * 30)
