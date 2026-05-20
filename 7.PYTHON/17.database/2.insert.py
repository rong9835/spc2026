import sqlite3

conn = sqlite3.connect('example.db')
cur = conn.cursor()

cur.execute('''
    INSERT INTO users (name, age) VALUES (?, ?)
''', ('Alice', 30))

cur.execute('''
    INSERT INTO users (name, age) VALUES ('Bob', 25)
''')

conn.commit()
conn.close()
