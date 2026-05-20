# pip install flask-sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=True)

    # 여기 밑에는 Flask 나 SQLAlchemy와는 무관한.. 파이썬 클래스를 출력할때, 그 출력 포멧을 내가 정의하는 커스텀 클래스 출력 포멧 정의
    def __repr__(self):
        return f'<User {self.id}, {self.name}, {self.age}>'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 우리의 db와 flask 앱을 연결
db.init_app(app)

@app.route('/')
def index():
    users = User.query.all()
    for user in users:
        print(user)

    return render_template('index.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        print('DB 초기화중...')
        db.create_all()

        if not User.query.first():   # 만약 사용자가 한명도 없으면??
            print('사용자 초기화...')
            user1 = User(name="user1", age=30)
            user2 = User(name="user2", age=33)
            user3 = User(name="user3", age=34)
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(user3)
            db.session.commit()
    
    app.run(debug=True)
