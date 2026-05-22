import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, g

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'board.db')
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with open(SCHEMA_FILE, mode='r', encoding='utf-8') as f:
                db.cursor().executescript(f.read())
            db.commit()
            print("Database initialized successfully.")
    else:
        # Check if posts table exists just in case
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
            if not cursor.fetchone():
                with open(SCHEMA_FILE, mode='r', encoding='utf-8') as f:
                    cursor.executescript(f.read())
                db.commit()
                print("Posts table created.")

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY id DESC')
    posts = cursor.fetchall()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['POST'])
def add_post():
    title = request.form.get('title', '').strip()
    message = request.form.get('message', '').strip()
    
    if not title or not message:
        # Simple validation error, redirect back
        return redirect(url_for('index'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO posts (title, message) VALUES (?, ?)', (title, message))
    db.commit()
    return redirect(url_for('index'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    db = get_db()
    cursor = db.cursor()
    
    # Check if post exists
    cursor.execute('SELECT likes FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    if not post:
        return jsonify({'success': False, 'error': 'Post not found'}), 404
        
    new_likes = post['likes'] + 1
    cursor.execute('UPDATE posts SET likes = ? WHERE id = ?', (new_likes, post_id))
    db.commit()
    return jsonify({'success': True, 'likes': new_likes})

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    
    # Check if post exists
    cursor.execute('SELECT id FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    if not post:
        return jsonify({'success': False, 'error': 'Post not found'}), 404
        
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    return jsonify({'success': True})

# Setup custom filter for pretty date formatting in jinja
@app.template_filter('datetimeformat')
def datetimeformat(value):
    # value is sqlite standard timestamp: 'YYYY-MM-DD HH:MM:SS'
    # Return custom format like: 'YYYY.MM.DD HH:MM'
    try:
        if not value:
            return ""
        # SQLite's CURRENT_TIMESTAMP defaults to UTC or system local depending on context.
        # Let's extract date and time nicely.
        # Format: 2026-05-21 02:34:29 -> 2026.05.21 02:34
        parts = value.split(' ')
        if len(parts) >= 2:
            date_part = parts[0].replace('-', '.')
            time_part = ':'.join(parts[1].split(':')[:2])
            return f"{date_part} {time_part}"
        return value
    except Exception:
        return value

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
