import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_app.db')

def get_db_connection():
    """
    SQLite 데이터베이스 연결을 생성하고 반환합니다.
    행(Row) 데이터를 사전(dict)처럼 이름으로 접근할 수 있도록 row_factory를 설정합니다.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # 외래 키(Foreign Key) 제약 조건 활성화
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    데이터베이스 테이블을 생성하고, 초보자가 바로 사용할 수 있는 기초 데이터를 추가(시딩)합니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 사용자 테이블 (users)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user', -- 'user' 또는 'admin'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. 음악 테이블 (songs) - 유튜브 비디오 ID를 기본 키로 사용
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        youtube_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        thumbnail_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. 댓글 테이블 (comments)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        youtube_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # 4. 좋아요 테이블 (likes) - 사용자당 한 노래에 한 번만 좋아요 가능
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS likes (
        user_id INTEGER NOT NULL,
        youtube_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, youtube_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE
    )
    ''')

    # 5. 해시태그 테이블 (hashtags) - 노래당 동일 해시태그 중복 방지
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hashtags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        youtube_id TEXT NOT NULL,
        tag TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(youtube_id, tag)
    )
    ''')

    # 6. 알림 테이블 (notifications)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,      -- 알림을 받을 사용자 (좋아요 누른 사람)
        sender_id INTEGER NOT NULL,    -- 댓글을 쓴 사용자 (유발자)
        youtube_id TEXT NOT NULL,      -- 관련 음악 ID
        comment_id INTEGER NOT NULL,   -- 관련 댓글 ID
        is_read INTEGER DEFAULT 0,     -- 0: 안 읽음, 1: 읽음
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE,
        FOREIGN KEY (comment_id) REFERENCES comments (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()

    # --- 초기 데이터 삽입 (시딩 - Seeding) ---
    
    # 1. 기본 회원 데이터 (관리자 & 일반 사용자)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pw = generate_password_hash('admin123')
        user_pw = generate_password_hash('user123')
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', admin_pw, 'admin'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('user1', user_pw, 'user'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('music_lover', user_pw, 'user'))
        conn.commit()
        print("기본 계정 생성 완료 (admin / user1 / music_lover)")

    # 2. 기본 음악 데이터 (YouTube MV)
    cursor.execute("SELECT COUNT(*) FROM songs")
    if cursor.fetchone()[0] == 0:
        songs_data = [
            (
                'nM0xDI5R50E', 
                '[MV] IU(아이유) _ BBIBBI(삐삐)', 
                '경쾌하고 힙한 비트의 곡으로, 관계에 있어 선을 넘지 말라는 경고의 메시지를 담고 있는 아이유의 명곡입니다.',
                'https://i.ytimg.com/vi/nM0xDI5R50E/hq720.jpg'
            ),
            (
                'gJTtAppw830', 
                "BTS (방탄소년단) 'Dynamite' Official MV", 
                '전 세계를 뒤흔든 방탄소년단의 밝고 경쾌한 디스코 팝 장르의 곡으로, 활력과 에너지를 불어넣어 줍니다.',
                'https://i.ytimg.com/vi/gJTtAppw830/hq720.jpg'
            ),
            (
                'pSUydWEqKwE', 
                "NewJeans (뉴진스) 'Ditto' Official MV (Side A)", 
                '몽환적이고 아련한 세련된 레트로 감성으로 전 세대의 향수를 자극하며 뜨거운 인기를 얻은 곡입니다.',
                'https://i.ytimg.com/vi/pSUydWEqKwE/hq720.jpg'
            )
        ]
        cursor.executemany("INSERT INTO songs (youtube_id, title, description, thumbnail_url) VALUES (?, ?, ?, ?)", songs_data)
        conn.commit()
        print("기본 음악 데이터 생성 완료")

        # 3. 기본 해시태그 추가
        # user1 = 2, music_lover = 3, admin = 1
        tags_data = [
            ('nM0xDI5R50E', 'iu', 1),
            ('nM0xDI5R50E', 'kpop', 2),
            ('nM0xDI5R50E', '삐삐', 3),
            ('gJTtAppw830', 'bts', 2),
            ('gJTtAppw830', 'kpop', 1),
            ('gJTtAppw830', 'disco', 3),
            ('pSUydWEqKwE', 'newjeans', 3),
            ('pSUydWEqKwE', 'ditto', 2),
            ('pSUydWEqKwE', 'nostalgia', 1)
        ]
        cursor.executemany("INSERT INTO hashtags (youtube_id, tag, user_id) VALUES (?, ?, ?)", tags_data)

        # 4. 기본 좋아요 추가
        # user1(2) -> Dynamite, BBIBBI
        # music_lover(3) -> Ditto, Dynamite
        # admin(1) -> BBIBBI
        likes_data = [
            (2, 'gJTtAppw830'),
            (2, 'nM0xDI5R50E'),
            (3, 'pSUydWEqKwE'),
            (3, 'gJTtAppw830'),
            (1, 'nM0xDI5R50E')
        ]
        cursor.executemany("INSERT INTO likes (user_id, youtube_id) VALUES (?, ?)", likes_data)

        # 5. 기본 댓글 추가
        comments_data = [
            ('gJTtAppw830', 2, '이 노래는 들을 때마다 온몸에 소름이 돋고 춤추고 싶어져요! 🕺✨'),
            ('gJTtAppw830', 3, '빌보드 1위 클래스... 들을 때마다 정말 자랑스러운 다이너마이트! 🔥'),
            ('nM0xDI5R50E', 1, '선 넘지 말라는 옐로우 카드 가사가 너무 위트 있고 아이유 목소리와 찰떡입니다.'),
            ('pSUydWEqKwE', 2, '겨울이나 비 오는 날에 들으면 감수성이 아주 풍부해지는 띵곡입니다 ㅠㅠ')
        ]
        cursor.executemany("INSERT INTO comments (youtube_id, user_id, content) VALUES (?, ?, ?)", comments_data)

        # 6. 기본 알림 추가 (유저들이 좋아요 누른 곡에 댓글 달렸을 때)
        # 예: user1(2)이 BBIBBI를 좋아했는데, admin(1)이 BBIBBI에 댓글을 달았음.
        # admin의 댓글 ID는 3번. 이를 user1에게 알림.
        cursor.execute("INSERT INTO notifications (user_id, sender_id, youtube_id, comment_id, is_read) VALUES (?, ?, ?, ?, ?)", (2, 1, 'nM0xDI5R50E', 3, 0))
        
        conn.commit()
        print("기본 관계 데이터(댓글, 해시태그, 좋아요, 알림) 시딩 완료")

    conn.close()

if __name__ == '__main__':
    # 독립적으로 실행하면 데이터베이스가 즉시 초기화됩니다.
    init_db()
    print("데이터베이스 초기화가 완료되었습니다!")
