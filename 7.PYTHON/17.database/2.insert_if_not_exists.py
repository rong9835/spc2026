import sqlite3

conn = sqlite3.connect('example.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM users')
count = cur.fetchone()[0]
print(count)

if count == 0:
    cur.execute('''
        INSERT INTO users (name, age) VALUES (?, ?)
    ''', ('Alice', 30))

    cur.execute('''
        INSERT INTO users (name, age) VALUES ('Bob', 25)
    ''')

    conn.commit()
else:
    print("이미 테이블에 데이터가 있습니다.")

conn.close()
