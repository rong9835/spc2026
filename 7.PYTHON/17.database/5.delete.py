import sqlite3

conn = sqlite3.connect('example.db')
cur = conn.cursor()

cur.execute('''
    DELETE FROM users WHERE name=?
''', ('Bob',))

conn.commit()
conn.close()
