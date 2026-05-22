"""
database.py
-----------
이 파일은 SQLite 데이터베이스를 다루는 모든 코드를 모아둔 곳입니다.

초보자 설명:
- SQLite 는 파일 하나(music.db)에 모든 데이터를 저장하는 아주 간단한 데이터베이스입니다.
- 별도 서버 설치가 필요 없어서 학습용으로 딱 좋습니다.
- "테이블"은 엑셀의 시트 한 장이라고 생각하면 됩니다. (행 = 데이터, 열 = 항목)
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

# 이 파일(database.py)이 있는 폴더 안에 music.db 파일을 만듭니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "music.db")


def get_connection():
    """
    데이터베이스에 연결합니다.

    - row_factory = sqlite3.Row 로 설정하면,
      조회 결과를 row["title"] 처럼 '이름'으로 꺼낼 수 있어 편합니다.
    - PRAGMA foreign_keys = ON 은 외래 키(연결 관계)를 지키도록 켜는 설정입니다.
      (예: 노래가 삭제되면 그 노래의 댓글도 같이 삭제되도록)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    프로그램을 처음 실행할 때 테이블을 만들고, 예시 데이터를 채워 넣습니다.
    이미 테이블이 있으면 다시 만들지 않습니다 (IF NOT EXISTS).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1) 회원 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL DEFAULT 'user',   -- 'user' 또는 'admin'
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2) 노래 테이블 (유튜브 영상 ID를 기본 키로 사용)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            youtube_id    TEXT PRIMARY KEY,
            title         TEXT NOT NULL,
            description   TEXT,
            thumbnail_url TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3) 댓글 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            youtube_id  TEXT NOT NULL,
            user_id     INTEGER NOT NULL,
            content     TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id)    REFERENCES users (id)         ON DELETE CASCADE
        )
    """)

    # 4) 좋아요 테이블 (한 사람이 한 노래에 한 번만 → user_id+youtube_id 를 기본 키로)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            user_id     INTEGER NOT NULL,
            youtube_id  TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, youtube_id),
            FOREIGN KEY (user_id)    REFERENCES users (id)         ON DELETE CASCADE,
            FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE
        )
    """)

    # 5) 해시태그 테이블 (같은 노래에 같은 태그가 중복되지 않도록 UNIQUE 설정)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hashtags (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            youtube_id  TEXT NOT NULL,
            tag         TEXT NOT NULL,
            user_id     INTEGER NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (youtube_id, tag),
            FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id)    REFERENCES users (id)         ON DELETE CASCADE
        )
    """)

    # 6) 알림 테이블
    #    - user_id    : 알림을 받을 사람 (그 노래에 좋아요를 누른 사람)
    #    - sender_id  : 댓글을 쓴 사람 (알림을 일으킨 사람)
    #    - is_read    : 0=안 읽음, 1=읽음
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            sender_id   INTEGER NOT NULL,
            youtube_id  TEXT NOT NULL,
            comment_id  INTEGER NOT NULL,
            is_read     INTEGER NOT NULL DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)    REFERENCES users (id)         ON DELETE CASCADE,
            FOREIGN KEY (sender_id)  REFERENCES users (id)         ON DELETE CASCADE,
            FOREIGN KEY (youtube_id) REFERENCES songs (youtube_id) ON DELETE CASCADE,
            FOREIGN KEY (comment_id) REFERENCES comments (id)      ON DELETE CASCADE
        )
    """)

    conn.commit()

    # 테이블이 비어 있을 때만 예시 데이터를 넣습니다.
    _seed_data(conn, cursor)

    conn.close()


def _seed_data(conn, cursor):
    """
    처음 실행될 때 화면이 비어 보이지 않도록 예시 데이터를 채웁니다.
    (회원 / 노래 / 좋아요 / 댓글 / 해시태그 / 알림)
    """
    # 이미 회원이 있으면 아무것도 하지 않고 끝냅니다.
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return

    # --- 회원 3명 (비밀번호는 안전하게 암호화해서 저장) ---
    admin_pw = generate_password_hash("admin123")
    user_pw = generate_password_hash("user123")
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        ("admin", admin_pw, "admin"),
    )
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        ("user1", user_pw, "user"),
    )
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        ("music_lover", user_pw, "user"),
    )

    # --- 노래 3곡 ---
    songs = [
        (
            "nM0xDI5R50E",
            "[MV] IU(아이유) _ BBIBBI(삐삐)",
            "관계에서 선을 넘지 말라는 메시지를 경쾌하게 풀어낸 아이유의 곡.",
            "https://i.ytimg.com/vi/nM0xDI5R50E/hq720.jpg",
        ),
        (
            "gJTtAppw830",
            "BTS (방탄소년단) 'Dynamite' Official MV",
            "전 세계를 사로잡은 방탄소년단의 밝고 경쾌한 디스코 팝.",
            "https://i.ytimg.com/vi/gJTtAppw830/hq720.jpg",
        ),
        (
            "pSUydWEqKwE",
            "NewJeans (뉴진스) 'Ditto' Official MV (Side A)",
            "몽환적이고 아련한 레트로 감성이 매력적인 뉴진스의 곡.",
            "https://i.ytimg.com/vi/pSUydWEqKwE/hq720.jpg",
        ),
    ]
    cursor.executemany(
        "INSERT INTO songs (youtube_id, title, description, thumbnail_url) VALUES (?, ?, ?, ?)",
        songs,
    )

    # --- 해시태그 (user_id: admin=1, user1=2, music_lover=3) ---
    hashtags = [
        ("nM0xDI5R50E", "아이유", 1),
        ("nM0xDI5R50E", "kpop", 2),
        ("gJTtAppw830", "bts", 2),
        ("gJTtAppw830", "신나는", 1),
        ("pSUydWEqKwE", "뉴진스", 3),
        ("pSUydWEqKwE", "레트로", 2),
    ]
    cursor.executemany(
        "INSERT INTO hashtags (youtube_id, tag, user_id) VALUES (?, ?, ?)",
        hashtags,
    )

    # --- 좋아요 ---
    likes = [
        (2, "gJTtAppw830"),  # user1 → Dynamite
        (2, "nM0xDI5R50E"),  # user1 → BBIBBI
        (3, "pSUydWEqKwE"),  # music_lover → Ditto
        (1, "nM0xDI5R50E"),  # admin → BBIBBI
    ]
    cursor.executemany(
        "INSERT INTO likes (user_id, youtube_id) VALUES (?, ?)",
        likes,
    )

    # --- 댓글 ---
    comments = [
        ("gJTtAppw830", 2, "들을 때마다 기분이 좋아지는 노래예요!"),
        ("nM0xDI5R50E", 1, "가사가 위트 있고 멜로디도 중독적이네요."),
        ("pSUydWEqKwE", 3, "비 오는 날 듣기 좋은 띵곡 ㅠㅠ"),
    ]
    cursor.executemany(
        "INSERT INTO comments (youtube_id, user_id, content) VALUES (?, ?, ?)",
        comments,
    )

    conn.commit()

    # --- 알림 예시 ---
    # user1(2)이 'BBIBBI'에 좋아요를 눌렀는데, admin(1)이 'BBIBBI'에 댓글을 달았습니다.
    # 위 댓글 목록에서 BBIBBI 댓글은 두 번째로 들어갔으므로 comment_id = 2 입니다.
    cursor.execute(
        """
        INSERT INTO notifications (user_id, sender_id, youtube_id, comment_id, is_read)
        VALUES (?, ?, ?, ?, 0)
        """,
        (2, 1, "nM0xDI5R50E", 2),
    )
    conn.commit()

    print("예시 데이터를 생성했습니다. (계정: admin/admin123, user1/user123, music_lover/user123)")


# 이 파일을 직접 실행하면 데이터베이스를 초기화합니다.
if __name__ == "__main__":
    init_db()
    print("데이터베이스 준비 완료!")
