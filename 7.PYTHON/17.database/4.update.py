import sqlite3

conn = sqlite3.connect('example.db')
cur = conn.cursor()

cur.execute('''
    UPDATE users SET age=? WHERE name=?
''', (33, 'Bob'))

conn.commit()
conn.close()
