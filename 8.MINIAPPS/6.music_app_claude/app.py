"""
app.py
------
Flask 웹 서버의 본체입니다. 사용자가 주소(URL)로 접속하면 어떤 화면을 보여줄지,
자바스크립트가 데이터를 요청하면 어떤 값을 돌려줄지 여기서 정합니다.

용어 정리:
- 라우트(route): 특정 주소(/, /song/... 등)에 연결된 함수.
- API: 화면(HTML) 대신 데이터(JSON)를 돌려주는 주소. 자바스크립트가 사용합니다.
- 세션(session): 로그인한 사용자가 누구인지 서버가 기억하는 작은 보관함.
"""

import sqlite3
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, session, redirect, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

import database
import youtube

app = Flask(__name__)
# 세션(로그인 정보)을 암호화하기 위한 비밀 키입니다.
# 실제 서비스라면 외부에 노출되지 않게 환경 변수로 관리해야 합니다. (학습용이라 직접 적음)
app.secret_key = "music_app_claude_secret_key"

# 서버가 켜질 때 데이터베이스(테이블 + 예시 데이터)를 준비합니다.
database.init_db()


# ==========================================================
#  도우미: 로그인/관리자 여부를 검사하는 데코레이터
# ==========================================================
def login_required(view):
    """
    이 표시(@login_required)가 붙은 함수는 '로그인한 사람'만 사용할 수 있습니다.
    로그인이 안 되어 있으면 로그인 페이지로 보냅니다.
    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_page"))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    """이 표시가 붙은 API 는 '관리자'만 사용할 수 있습니다."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"success": False, "message": "관리자 권한이 필요합니다."}), 403
        return view(*args, **kwargs)
    return wrapper


# ==========================================================
#  화면(페이지) 라우트
# ==========================================================
@app.route("/")
def index():
    """메인 화면: 등록된 노래 목록 + 검색 + 인기 해시태그."""
    query = request.args.get("q", "").strip()
    conn = database.get_connection()

    # 1) 화면 위쪽에 보여줄 인기 해시태그 (많이 쓰인 순서 15개)
    popular_tags = conn.execute("""
        SELECT tag, COUNT(*) AS count
        FROM hashtags
        GROUP BY tag
        ORDER BY count DESC
        LIMIT 15
    """).fetchall()

    # 2) 노래 목록 가져오기 (검색어가 있으면 제목/설명/해시태그에서 찾음)
    if query:
        like = f"%{query}%"
        tag_query = query.replace("#", "")  # '#락' 으로 검색해도 '락' 으로 찾도록
        rows = conn.execute("""
            SELECT DISTINCT s.*,
                (SELECT COUNT(*) FROM likes    WHERE youtube_id = s.youtube_id) AS like_count,
                (SELECT COUNT(*) FROM comments WHERE youtube_id = s.youtube_id) AS comment_count
            FROM songs s
            LEFT JOIN hashtags h ON s.youtube_id = h.youtube_id
            WHERE s.title LIKE ? OR s.description LIKE ? OR h.tag LIKE ?
            ORDER BY s.created_at DESC
        """, (like, like, f"%{tag_query}%")).fetchall()
    else:
        rows = conn.execute("""
            SELECT s.*,
                (SELECT COUNT(*) FROM likes    WHERE youtube_id = s.youtube_id) AS like_count,
                (SELECT COUNT(*) FROM comments WHERE youtube_id = s.youtube_id) AS comment_count
            FROM songs s
            ORDER BY s.created_at DESC
        """).fetchall()

    # 3) 각 노래에 해시태그 목록과 '내가 좋아요 했는지'를 붙입니다.
    songs = []
    for row in rows:
        song = dict(row)
        tag_rows = conn.execute(
            "SELECT tag FROM hashtags WHERE youtube_id = ?", (song["youtube_id"],)
        ).fetchall()
        song["tags"] = [t["tag"] for t in tag_rows]
        song["is_liked"] = _is_liked(conn, song["youtube_id"])
        songs.append(song)

    conn.close()
    return render_template("index.html", songs=songs, tags=popular_tags, query=query)


@app.route("/song/<youtube_id>")
def song_detail(youtube_id):
    """노래 상세 화면: 영상 재생 + 좋아요 + 해시태그 + 댓글."""
    conn = database.get_connection()

    song = conn.execute(
        "SELECT * FROM songs WHERE youtube_id = ?", (youtube_id,)
    ).fetchone()
    if song is None:
        conn.close()
        return "등록되지 않은 노래입니다.", 404

    like_count = conn.execute(
        "SELECT COUNT(*) FROM likes WHERE youtube_id = ?", (youtube_id,)
    ).fetchone()[0]
    is_liked = _is_liked(conn, youtube_id)

    hashtags = conn.execute("""
        SELECT h.tag, u.username
        FROM hashtags h
        JOIN users u ON h.user_id = u.id
        WHERE h.youtube_id = ?
        ORDER BY h.created_at ASC
    """, (youtube_id,)).fetchall()

    comments = conn.execute("""
        SELECT c.id, c.content, c.created_at, u.username, u.role
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.youtube_id = ?
        ORDER BY c.created_at ASC
    """, (youtube_id,)).fetchall()

    conn.close()
    return render_template(
        "song_detail.html",
        song=song,
        like_count=like_count,
        is_liked=is_liked,
        hashtags=hashtags,
        comments=comments,
    )


@app.route("/auth")
def auth_page():
    """로그인 / 회원가입 화면. 이미 로그인했으면 메인으로 보냅니다."""
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("auth.html")


@app.route("/profile")
@login_required
def profile_page():
    """내 프로필: 내가 쓴 댓글 + 내가 좋아요한 노래 + 내 알림 목록."""
    conn = database.get_connection()
    user_id = session["user_id"]

    my_comments = conn.execute("""
        SELECT c.content, c.created_at, s.title AS song_title, s.youtube_id
        FROM comments c
        JOIN songs s ON c.youtube_id = s.youtube_id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    """, (user_id,)).fetchall()

    my_likes = conn.execute("""
        SELECT s.*,
            (SELECT COUNT(*) FROM likes WHERE youtube_id = s.youtube_id) AS like_count
        FROM likes l
        JOIN songs s ON l.youtube_id = s.youtube_id
        WHERE l.user_id = ?
        ORDER BY l.created_at DESC
    """, (user_id,)).fetchall()

    my_notifications = conn.execute("""
        SELECT n.is_read, n.created_at,
               sender.username AS sender_name,
               s.title AS song_title, s.youtube_id,
               c.content AS comment_content
        FROM notifications n
        JOIN users sender   ON n.sender_id  = sender.id
        JOIN songs s        ON n.youtube_id = s.youtube_id
        JOIN comments c     ON n.comment_id = c.id
        WHERE n.user_id = ?
        ORDER BY n.created_at DESC
    """, (user_id,)).fetchall()

    conn.close()
    return render_template(
        "profile.html",
        comments=my_comments,
        likes=my_likes,
        notifications=my_notifications,
    )


@app.route("/admin")
@login_required
def admin_page():
    """관리자 화면: 회원/노래/댓글 관리. 관리자가 아니면 메인으로 보냅니다."""
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    conn = database.get_connection()

    users = conn.execute(
        "SELECT id, username, role, created_at FROM users ORDER BY id ASC"
    ).fetchall()

    songs = conn.execute("""
        SELECT s.*,
            (SELECT COUNT(*) FROM likes    WHERE youtube_id = s.youtube_id) AS like_count,
            (SELECT COUNT(*) FROM comments WHERE youtube_id = s.youtube_id) AS comment_count
        FROM songs s
        ORDER BY s.created_at DESC
    """).fetchall()

    comments = conn.execute("""
        SELECT c.id, c.content, c.created_at, u.username, s.title AS song_title
        FROM comments c
        JOIN users u ON c.user_id = u.id
        JOIN songs s ON c.youtube_id = s.youtube_id
        ORDER BY c.created_at DESC
    """).fetchall()

    conn.close()
    return render_template("admin.html", users=users, songs=songs, comments=comments)


# ==========================================================
#  인증 API (회원가입 / 로그인 / 로그아웃)
# ==========================================================
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "아이디와 비밀번호를 모두 입력해 주세요."}), 400
    if len(username) < 3:
        return jsonify({"success": False, "message": "아이디는 3글자 이상이어야 합니다."}), 400
    if len(password) < 4:
        return jsonify({"success": False, "message": "비밀번호는 4글자 이상이어야 합니다."}), 400

    conn = database.get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        conn.commit()
        return jsonify({"success": True, "message": "회원가입 성공! 이제 로그인해 주세요."})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "이미 사용 중인 아이디입니다."}), 400
    finally:
        conn.close()


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = database.get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        # 로그인 성공 → 세션에 사용자 정보를 기억시킵니다.
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        return jsonify({"success": True, "message": f"{username}님 환영합니다!"})

    return jsonify({"success": False, "message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401


@app.route("/api/logout")
def api_logout():
    session.clear()  # 세션 비우기 = 로그아웃
    return redirect(url_for("index"))


# ==========================================================
#  유튜브 검색 + 노래 등록 API
# ==========================================================
@app.route("/api/youtube/search")
def api_youtube_search():
    """검색어로 유튜브를 검색해 결과(JSON)를 돌려줍니다."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    return jsonify(youtube.search_youtube(query))


@app.route("/api/songs", methods=["POST"])
@login_required
def api_add_song():
    """유튜브 검색 결과(또는 영상 주소)를 우리 사이트에 노래로 등록합니다."""
    data = request.get_json() or {}
    raw_id = data.get("youtube_id", "").strip()
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    thumbnail_url = data.get("thumbnail_url", "").strip()

    # 사용자가 영상 주소(URL)를 붙여넣었을 수도 있으니 ID만 뽑아냅니다.
    youtube_id = youtube.extract_video_id(raw_id)
    if not youtube_id:
        return jsonify({"success": False, "message": "올바른 유튜브 주소가 아닙니다."}), 400

    # 제목/썸네일 정보가 없으면 기본값을 채워 넣습니다.
    if not title:
        title = f"유튜브 음악 ({youtube_id})"
    if not thumbnail_url:
        thumbnail_url = f"https://i.ytimg.com/vi/{youtube_id}/hqdefault.jpg"

    conn = database.get_connection()
    try:
        conn.execute(
            "INSERT INTO songs (youtube_id, title, description, thumbnail_url) VALUES (?, ?, ?, ?)",
            (youtube_id, title, description, thumbnail_url),
        )
        conn.commit()
        return jsonify({"success": True, "youtube_id": youtube_id, "message": "노래가 등록되었습니다!"})
    except sqlite3.IntegrityError:
        # 이미 있는 노래면 오류 대신 그 노래로 안내합니다.
        return jsonify({"success": True, "youtube_id": youtube_id, "already_exists": True,
                        "message": "이미 등록된 노래입니다."})
    finally:
        conn.close()


# ==========================================================
#  좋아요 / 댓글 / 해시태그 API
# ==========================================================
@app.route("/api/songs/<youtube_id>/like", methods=["POST"])
@login_required
def api_toggle_like(youtube_id):
    """좋아요 누르기/취소하기 (한 번 더 누르면 취소)."""
    user_id = session["user_id"]
    conn = database.get_connection()

    exists = conn.execute(
        "SELECT 1 FROM likes WHERE user_id = ? AND youtube_id = ?",
        (user_id, youtube_id),
    ).fetchone()

    if exists:
        conn.execute(
            "DELETE FROM likes WHERE user_id = ? AND youtube_id = ?",
            (user_id, youtube_id),
        )
        liked = False
    else:
        conn.execute(
            "INSERT INTO likes (user_id, youtube_id) VALUES (?, ?)",
            (user_id, youtube_id),
        )
        liked = True
    conn.commit()

    count = conn.execute(
        "SELECT COUNT(*) FROM likes WHERE youtube_id = ?", (youtube_id,)
    ).fetchone()[0]
    conn.close()

    return jsonify({"success": True, "liked": liked, "like_count": count})


@app.route("/api/songs/<youtube_id>/comments", methods=["POST"])
@login_required
def api_add_comment(youtube_id):
    """
    댓글을 답니다. 그리고 이 노래에 '좋아요'를 누른 다른 사람들에게 알림을 보냅니다.
    (= 내가 좋아요 한 음악에 남이 댓글 달면 나에게 알림이 오는 기능)
    """
    content = (request.get_json() or {}).get("content", "").strip()
    if not content:
        return jsonify({"success": False, "message": "댓글 내용을 입력해 주세요."}), 400

    user_id = session["user_id"]
    conn = database.get_connection()

    # 1) 댓글 저장
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comments (youtube_id, user_id, content) VALUES (?, ?, ?)",
        (youtube_id, user_id, content),
    )
    comment_id = cursor.lastrowid

    # 2) 이 노래를 좋아요한 사람들에게 알림 만들기 (단, 댓글 쓴 본인은 제외)
    liked_users = conn.execute(
        "SELECT user_id FROM likes WHERE youtube_id = ? AND user_id != ?",
        (youtube_id, user_id),
    ).fetchall()
    for row in liked_users:
        conn.execute(
            """
            INSERT INTO notifications (user_id, sender_id, youtube_id, comment_id)
            VALUES (?, ?, ?, ?)
            """,
            (row["user_id"], user_id, youtube_id, comment_id),
        )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "comment": {
            "username": session["username"],
            "content": content,
            "created_at": "방금 전",
        },
    })


@app.route("/api/songs/<youtube_id>/hashtags", methods=["POST"])
@login_required
def api_add_hashtag(youtube_id):
    """노래에 해시태그를 자유롭게 추가합니다."""
    tag = (request.get_json() or {}).get("tag", "").strip().lstrip("#").lower()

    if not tag:
        return jsonify({"success": False, "message": "해시태그를 입력해 주세요."}), 400
    if len(tag) > 20:
        return jsonify({"success": False, "message": "해시태그는 20자 이하로 입력해 주세요."}), 400

    conn = database.get_connection()
    try:
        conn.execute(
            "INSERT INTO hashtags (youtube_id, tag, user_id) VALUES (?, ?, ?)",
            (youtube_id, tag, session["user_id"]),
        )
        conn.commit()
        return jsonify({"success": True, "tag": tag, "username": session["username"]})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "이미 추가된 해시태그입니다."}), 400
    finally:
        conn.close()


# ==========================================================
#  알림 API (프로필 화면 / 상단 종 아이콘에서 사용)
# ==========================================================
@app.route("/api/notifications")
@login_required
def api_get_notifications():
    """읽지 않은 알림 개수와 목록을 돌려줍니다. (자바스크립트가 주기적으로 확인)"""
    user_id = session["user_id"]
    conn = database.get_connection()
    rows = conn.execute("""
        SELECT n.id, sender.username AS sender_name,
               s.title AS song_title, s.youtube_id, c.content AS comment_content
        FROM notifications n
        JOIN users sender ON n.sender_id  = sender.id
        JOIN songs s      ON n.youtube_id = s.youtube_id
        JOIN comments c   ON n.comment_id = c.id
        WHERE n.user_id = ? AND n.is_read = 0
        ORDER BY n.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()

    notifications = [{
        "sender_name": r["sender_name"],
        "song_title": r["song_title"],
        "youtube_id": r["youtube_id"],
        "comment_content": r["comment_content"],
    } for r in rows]

    return jsonify({"success": True, "unread_count": len(notifications),
                    "notifications": notifications})


@app.route("/api/notifications/read", methods=["POST"])
@login_required
def api_mark_notifications_read():
    """내 알림을 모두 '읽음'으로 표시합니다."""
    conn = database.get_connection()
    conn.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = ?",
        (session["user_id"],),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ==========================================================
#  관리자 전용 API (회원/노래/댓글 관리)
# ==========================================================
@app.route("/api/admin/users/<int:user_id>/role", methods=["POST"])
@login_required
@admin_required
def api_admin_toggle_role(user_id):
    """회원 등급을 일반↔관리자 로 바꿉니다. (자기 자신은 바꿀 수 없음)"""
    if user_id == session["user_id"]:
        return jsonify({"success": False, "message": "자기 자신의 등급은 바꿀 수 없습니다."}), 400

    conn = database.get_connection()
    user = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        conn.close()
        return jsonify({"success": False, "message": "존재하지 않는 회원입니다."}), 404

    new_role = "admin" if user["role"] == "user" else "user"
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "new_role": new_role})


@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
@login_required
@admin_required
def api_admin_delete_user(user_id):
    """회원을 강제로 탈퇴(삭제)시킵니다. (자기 자신은 삭제 불가)"""
    if user_id == session["user_id"]:
        return jsonify({"success": False, "message": "자기 자신은 삭제할 수 없습니다."}), 400

    conn = database.get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/admin/songs/<youtube_id>", methods=["DELETE"])
@login_required
@admin_required
def api_admin_delete_song(youtube_id):
    """노래(게시글)를 삭제합니다. 관련 댓글/좋아요/태그도 함께 삭제됩니다."""
    conn = database.get_connection()
    conn.execute("DELETE FROM songs WHERE youtube_id = ?", (youtube_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/admin/comments/<int:comment_id>", methods=["DELETE"])
@login_required
@admin_required
def api_admin_delete_comment(comment_id):
    """부적절한 댓글을 삭제합니다."""
    conn = database.get_connection()
    conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ==========================================================
#  작은 도우미 함수
# ==========================================================
def _is_liked(conn, youtube_id):
    """현재 로그인한 사용자가 이 노래에 좋아요를 눌렀는지 True/False 로 돌려줍니다."""
    if "user_id" not in session:
        return False
    row = conn.execute(
        "SELECT 1 FROM likes WHERE user_id = ? AND youtube_id = ?",
        (session["user_id"], youtube_id),
    ).fetchone()
    return row is not None


# 이 파일을 직접 실행했을 때만 서버를 켭니다.
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
