import sqlite3

def connect_db():
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()
    return conn, cur

def disconnect_db(conn):
    conn.commit()
    conn.close()

def create_table():
    conn, cur = connect_db()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL)
        ''')
    disconnect_db(conn)

def insert_user(name, age):
    conn, cur = connect_db()
    cur.execute('INSERT INTO users (name, age) VALUES (?, ?)', (name, age))
    disconnect_db(conn)

def get_users():
    conn, cur = connect_db()
    cur.execute('SELECT * FROM users')
    rows = cur.fetchall() # 모두
    disconnect_db(conn)
    return rows

def get_user_by_name(name):
    conn, cur = connect_db()
    cur.execute('SELECT * FROM users WHERE name=?', (name ,))
    user = cur.fetchone() # 한명만 (동명이인 있으면 여러명 나올수 있어서 사실은 fetchall() 해야함)
    disconnect_db(conn)
    return user

def update_user(name, new_age):
    conn, cur = connect_db()
    cur.execute('UPDATE users SET age=? WHERE name=?', (new_age, name))
    disconnect_db(conn)

def delete_user_by_name(name):
    conn, cur = connect_db()
    cur.execute('DELETE FROM users WHERE name=?', (name, ))
    disconnect_db(conn)

def delete_user_by_id(id):
    conn, cur = connect_db()
    cur.execute('DELETE FROM users WHERE id=?', (id, ))
    disconnect_db(conn)
