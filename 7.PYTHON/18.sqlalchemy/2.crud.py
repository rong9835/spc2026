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

# CRUD 수행할 함수 구현
def create_user(session, name, age):
    new_user = User(name=name, age=age)
    session.add(new_user)
    session.commit()
    return new_user

def list_users(session):
    users = session.query(User).all()
    return users

def get_user_by_id(session, user_id):
    # SELECT * FROM users WHERE id=userid

    # 원래 하던 직관적인 alchemy 스타일 코드
    # user = session.query(User).filter_by(id=user_id).first()
    # return user
    # 아래는 modern 한 스타일 코드
    return session.get(User, user_id)

def update_user_age(session, user_id, new_age):
    user = session.get(User, user_id)
    if not user:
        return False
    user.age = new_age
    session.commit()
    return True

def delete_user_by_id(session, user_id):
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True

def delete_user_by_name(session, name):
    # user = session.get(User, user.name)
    # SELECT * FROM users WHERE name=name
    users = session.query(User).filter_by(name=name).all()
    if not users:
        return 0
    
    for user in users:
        session.delete(user)
    session.commit()
    return len(users)  # 삭제된 사람의 갯수를 반환

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    with Session() as session:
        # 1) 사용자 생성
        hong = create_user(session, "홍길동", 22)
        kim = create_user(session, "김길동", 33)
        print(f"추가된 사용자들: {hong.id}, {kim.id}")

        # 2) 사용자 조회
        user = get_user_by_id(session, hong.id)
        print(f"조회한 사람은: {user.id}, {user.name}")

        users = list_users(session)
        print("전체 사용자 조회")
        for u in users:
            print(f" - {u.id}: {u.name}, {u.age}")

        # 3) 사용자 정보 수정
        updated_user = update_user_age(session, kim.id, 44)
        user = get_user_by_id(session, kim.id)
        print(f"조회한 사람은: {user.id}, {user.name}, {user.age}")

        users = list_users(session)
        print("전체 사용자 조회")
        for u in users:
            print(f" - {u.id}: {u.name}, {u.age}")

        # 4) 사용자 삭제
        deleted_user_count = delete_user_by_name(session, "홍길동")
        print(f"삭제된 사용자 수는: {deleted_user_count}")

        users = list_users(session)
        print("전체 사용자 조회")
        for u in users:
            print(f" - {u.id}: {u.name}, {u.age}")