from flask import Flask, render_template, request
from flask import redirect, url_for
from flask import session, flash

from datetime import timedelta

import sqlite3

app = Flask(__name__)
app.secret_key = 'hello1234'  # 실무적으로는 이런 민감한 credential 을 커밋하지 않음.
app.permanent_session_lifetime = timedelta(minutes=5)

DATABASE = 'users.sqlite3'  # 나의 파일명


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 나의 결과를 다 Dict 포멧으로 관리
    # row[0] => row['id'] 이런식으로 접근 가능
    return conn


def init_db():
    with app.app_context():  # flask app 초기화 완료된 후
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT
            )""")

        # 기본 계정 추가
        cur.execute('SELECT COUNT(*) AS count FROM users')
        count = cur.fetchone()['count']
        if count == 0:
            cur.execute(
                'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                ('user1', 'password1', 'user1@example.com'),
            )
            cur.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                ('user2', 'password2'),
            )

        # 부팅시 계정 정보 출력
        cur.execute('SELECT * FROM users')
        rows = cur.fetchall()

        print('-' * 30)
        for row in rows:
            print(
                row['id'], row['username'], row['password'], row['email']
            )  # 이건 다 Row 를 Dict로 했기 때문에 이름으로 접근 가능
        print('-' * 30)

        conn.commit()
        conn.close()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/profile', methods=['POST'])
def profile_edit():
    # 사용자가 입력한 정보를 가져온다
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    conn = get_db_connection()
    cur = conn.cursor()

    if password:
        cur.execute(
            'UPDATE users SET password=? WHERE username=?', (password, username)
        )
    if email:
        cur.execute('UPDATE users SET email=? WHERE username=?', (email, username))

    conn.commit()
    flash('정상적으로 수정되었습니다.')

    # 입력한 정보중 있는것을 골라서 수정한다
    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    # 1. DB에서 나의 정보를 조회한다. (세션에 있음!!!)
    # 2. 그래서 아래에 넘겨줒다.
    # 3. 해당 정보에 수정기능을 넣는다.
    username = session.get('user', None)
    if username:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username=?', (username,))
        user = cur.fetchone()
        print(user)
    else:
        flash('로그인을 필요로 합니다.')
        return redirect(url_for('signin'))

    return render_template('profile.html', user=user)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        conn = get_db_connection()
        cur = conn.cursor()
        # 추가 하기 전, 해당 id를 가진 사용자가 있는지 확인
        cur.execute('SELECT * FROM users WHERE username=?', (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('해당 ID는 사용할 수 없습니다.')
            conn.close()
            return redirect(url_for('signin'))

        cur.execute(
            'INSERT INTO users (username, password, email) VALUES (?,?,?)',
            (username, password, email),
        )
        conn.commit()
        conn.close()

        flash('회원가입이 성공적으로 완료되었습니다.')
        return redirect(url_for('login'))

    return render_template('signin.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM users WHERE username=? AND password=?', (username, password)
        )
        user_data = cur.fetchone()
        conn.close()

        if user_data:
            session['user'] = username
            flash('로그인에 성공하였습니다.')
            return redirect(url_for('home'))
        else:
            flash('로그인에 실패하였습니다.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    flash('성공적으로 로그아웃이 되었습니다.')
    session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)  # 실무적으로는 꼭~~~ 끌것
