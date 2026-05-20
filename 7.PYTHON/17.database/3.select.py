import sqlite3

conn = sqlite3.connect('example.db')
cur = conn.cursor()

cur.execute('SELECT * FROM users')

# 커서야.. 니가 실행한 결과 다 나 줘..
rows = cur.fetchall()
print(rows)

conn.close()
