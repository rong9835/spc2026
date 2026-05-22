from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import re
import json
import requests
from werkzeug.security import check_password_hash, generate_password_hash
import database

app = Flask(__name__)
# Flask 세션 암호화 키 설정 (보안상 랜덤 키를 사용하는 것이 좋습니다)
app.secret_key = 'beatspace_secret_key_for_session_management'

# 앱 시작 시 데이터베이스 초기화
database.init_db()

# --- 유튜브 검색 스크래퍼 (API 키 불필요) ---
def youtube_live_search(query):
    """
    유튜브 검색 페이지(https://www.youtube.com/results)를 요청하여
    HTML 내부의 ytInitialData JSON 데이터에서 동영상 정보를 추출합니다.
    """
    url = f'https://www.youtube.com/results?search_query={query}'
    headers = {
        # 브라우저처럼 보이기 위한 User-Agent 설정
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        
        # ytInitialData 변수의 JSON 내용 찾기
        pattern = r'var ytInitialData = ({.*?});'
        match = re.search(pattern, response.text)
        if not match:
            return []
        
        data = json.loads(match.group(1))
        # 유튜브 JSON 경로 탐색 (실제 검색 결과 목록)
        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
        
        videos = []
        for section in contents:
            if 'itemSectionRenderer' in section:
                items = section['itemSectionRenderer']['contents']
                for item in items:
                    if 'videoRenderer' in item:
                        v = item['videoRenderer']
                        video_id = v.get('videoId')
                        # 동영상 제목
                        title = v.get('title', {}).get('runs', [{}])[0].get('text', '')
                        # 동영상 설명
                        desc_runs = v.get('detailedMetadataSnippets', [{}])[0].get('snippetText', {}).get('runs', [])
                        description = ''.join([run.get('text', '') for run in desc_runs]) if desc_runs else ''
                        if not description:
                            desc_runs = v.get('descriptionSnippet', {}).get('runs', [])
                            description = ''.join([run.get('text', '') for run in desc_runs])
                        # 썸네일 URL
                        thumbnail = v.get('thumbnail', {}).get('thumbnails', [{}])[0].get('url', '')
                        
                        if video_id and title:
                            videos.append({
                                'id': video_id,
                                'title': title,
                                'description': description,
                                'thumbnail': thumbnail
                            })
        return videos[:10]  # 상위 10개 결과 반환
    except Exception as e:
        print(f"유튜브 검색 오류: {e}")
        return []

# --- 데코레이터: 로그인 필수 검사 ---
def login_required(f):
    """
    로그인이 완료된 사용자인지 검증하는 데코레이터입니다.
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 로그인이 안 되어 있다면 로그인 페이지로 리다이렉트
            return redirect(url_for('auth_page'))
        return f(*args, **kwargs)
    return decorated_function

# --- 데코레이터: 관리자 권한 필수 검사 ---
def admin_required(f):
    """
    관리자 권한을 가진 사용자인지 검증하는 데코레이터입니다.
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
#                  뷰 라우트
# ==========================================

@app.route('/')
def index():
    """
    메인 페이지: 등록된 음악 목록(검색 필터 적용 가능), 핫 해시태그 목록 등을 보여줍니다.
    """
    query = request.args.get('q', '').strip()
    conn = database.get_db_connection()
    
    # 1. 태그 클라우드용 전체 해시태그 목록 가져오기 (가장 많이 사용된 태그 순)
    tags_rows = conn.execute('''
        SELECT tag, COUNT(*) as count 
        FROM hashtags 
        GROUP BY tag 
        ORDER BY count DESC 
        LIMIT 15
    ''').fetchall()
    
    # 2. 로컬 음악 검색 및 목록 가져오기 (제목, 설명, 해시태그 복합 검색)
    if query:
        search_query = f"%{query}%"
        # 해시태그에서 '#' 문자를 떼어내고 검색할 수 있도록 함
        clean_tag = query.replace('#', '')
        
        songs_rows = conn.execute('''
            SELECT DISTINCT s.*, 
                (SELECT COUNT(*) FROM likes WHERE youtube_id = s.youtube_id) AS like_count,
                (SELECT COUNT(*) FROM comments WHERE youtube_id = s.youtube_id) AS comment_count
            FROM songs s
            LEFT JOIN hashtags h ON s.youtube_id = h.youtube_id
            WHERE s.title LIKE ? 
               OR s.description LIKE ? 
               OR h.tag LIKE ?
            ORDER BY like_count DESC
        ''', (search_query, search_query, clean_tag)).fetchall()
    else:
        # 검색어가 없을 때는 최신 순 혹은 인기 순으로 목록 출력
        songs_rows = conn.execute('''
            SELECT s.*, 
                (SELECT COUNT(*) FROM likes WHERE youtube_id = s.youtube_id) AS like_count,
                (SELECT COUNT(*) FROM comments WHERE youtube_id = s.youtube_id) AS comment_count
            FROM songs s
            ORDER BY created_at DESC
        ''').fetchall()
    
    # 3. 각 음악 카드별로 해시태그 목록 가져와 딕셔너리로 저장
    songs = []
    for row in songs_rows:
        song = dict(row)
        # 해당 음악의 해시태그 가져오기
        hashtag_rows = conn.execute('SELECT tag FROM hashtags WHERE youtube_id = ?', (song['youtube_id'],)).fetchall()
        song['tags'] = [h['tag'] for h in hashtag_rows]
        
        # 현재 세션 사용자의 좋아요 여부 파악
        song['is_liked'] = False
        if 'user_id' in session:
            like_exists = conn.execute('''
                SELECT 1 FROM likes WHERE user_id = ? AND youtube_id = ?
            ''', (session['user_id'], song['youtube_id'])).fetchone()
            if like_exists:
                song['is_liked'] = True
                
        songs.append(song)
        
    conn.close()
    return render_template('index.html', songs=songs, tags=tags_rows, query=query)


@app.route('/song/<youtube_id>')
def song_detail(youtube_id):
    """
    음악 상세정보 페이지: 유튜브 동영상 재생기, 좋아요 개수, 사용자별 해시태그 리스트, 댓글 목록 출력
    """
    conn = database.get_db_connection()
    
    # 1. 음악 상세 정보 가져오기
    song_row = conn.execute('SELECT * FROM songs WHERE youtube_id = ?', (youtube_id,)).fetchone()
    if not song_row:
        conn.close()
        return "존재하지 않거나 등록되지 않은 음악입니다.", 404
        
    song = dict(song_row)
    
    # 2. 좋아요 개수 및 로그인한 사용자의 좋아요 상태 조회
    like_count = conn.execute('SELECT COUNT(*) FROM likes WHERE youtube_id = ?', (youtube_id,)).fetchone()[0]
    is_liked = False
    if 'user_id' in session:
        like_exists = conn.execute('SELECT 1 FROM likes WHERE user_id = ? AND youtube_id = ?', (session['user_id'], youtube_id)).fetchone()
        is_liked = like_exists is not None
        
    # 3. 등록된 해시태그 가져오기
    hashtag_rows = conn.execute('''
        SELECT h.*, u.username 
        FROM hashtags h 
        JOIN users u ON h.user_id = u.id 
        WHERE h.youtube_id = ?
    ''', (youtube_id,)).fetchall()
    
    # 4. 등록된 댓글 목록 가져오기 (오래된 순)
    comment_rows = conn.execute('''
        SELECT c.*, u.username, u.role
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.youtube_id = ?
        ORDER BY c.created_at ASC
    ''', (youtube_id,)).fetchall()
    
    conn.close()
    return render_template('song_detail.html', song=song, like_count=like_count, is_liked=is_liked, hashtags=hashtag_rows, comments=comment_rows)


@app.route('/auth')
def auth_page():
    """
    로그인 / 회원가입 페이지
    """
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('auth.html')


@app.route('/profile')
@login_required
def profile_page():
    """
    마이 프로필 페이지: 작성한 댓글 목록, 좋아요 한 음악 목록, 알림 히스토리 확인 가능
    """
    conn = database.get_db_connection()
    user_id = session['user_id']
    
    # 1. 내가 남긴 댓글 목록 조회
    my_comments = conn.execute('''
        SELECT c.*, s.title as song_title, s.thumbnail_url
        FROM comments c
        JOIN songs s ON c.youtube_id = s.youtube_id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    ''', (user_id,)).fetchall()
    
    # 2. 내가 좋아요 한 음악 목록 조회
    my_likes = conn.execute('''
        SELECT s.*, 
            (SELECT COUNT(*) FROM likes WHERE youtube_id = s.youtube_id) AS like_count,
            (SELECT COUNT(*) FROM comments WHERE youtube_id = s.youtube_id) AS comment_count
        FROM likes l
        JOIN songs s ON l.youtube_id = s.youtube_id
        WHERE l.user_id = ?
        ORDER BY l.created_at DESC
    ''', (user_id,)).fetchall()
    
    # 3. 전체 알림 목록 조회
    my_notifications = conn.execute('''
        SELECT n.*, sender.username as sender_name, s.title as song_title, c.content as comment_content
        FROM notifications n
        JOIN users sender ON n.sender_id = sender.id
        JOIN songs s ON n.youtube_id = s.youtube_id
        JOIN comments c ON n.comment_id = c.id
        WHERE n.user_id = ?
        ORDER BY n.created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('profile.html', comments=my_comments, likes=my_likes, notifications=my_notifications)


@app.route('/admin')
@login_required
def admin_page():
    """
    관리자 페이지: 회원관리, 노래관리, 댓글관리 전체 현황을 탭으로 볼 수 있는 통합 관리자 센터
    """
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
        
    conn = database.get_db_connection()
    
    # 1. 회원 전체 목록 조회
    users_list = conn.execute('SELECT id, username, role, created_at FROM users ORDER BY id ASC').fetchall()
    
    # 2. 등록된 음악 전체 목록 조회
    songs_list = conn.execute('''
        SELECT s.*, 
            (SELECT COUNT(*) FROM likes WHERE youtube_id = s.youtube_id) AS like_count,
            (SELECT COUNT(*) FROM comments WHERE youtube_id = s.youtube_id) AS comment_count
        FROM songs s
        ORDER BY s.created_at DESC
    ''').fetchall()
    
    # 3. 전체 댓글 목록 조회
    comments_list = conn.execute('''
        SELECT c.*, u.username, s.title as song_title
        FROM comments c
        JOIN users u ON c.user_id = u.id
        JOIN songs s ON c.youtube_id = s.youtube_id
        ORDER BY c.created_at DESC
    ''').fetchall()
    
    conn.close()
    return render_template('admin.html', users=users_list, songs=songs_list, comments=comments_list)


# ==========================================
#               REST API 라우트
# ==========================================

# --- 인증 API ---

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '아이디와 비밀번호를 모두 입력해 주세요.'}), 400
        
    if len(username) < 3:
        return jsonify({'success': False, 'message': '아이디는 3글자 이상이어야 합니다.'}), 400
        
    conn = database.get_db_connection()
    try:
        # 비밀번호 해싱 후 데이터 저장
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return jsonify({'success': True, 'message': '회원가입에 성공했습니다! 이제 로그인해 주세요.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '이미 사용 중인 아이디입니다.'}), 400
    finally:
        conn.close()


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '아이디와 비밀번호를 모두 입력해 주세요.'}), 400
        
    conn = database.get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user_row and check_password_hash(user_row['password'], password):
        # 세션에 정보 기록
        session['user_id'] = user_row['id']
        session['username'] = user_row['username']
        session['role'] = user_row['role']
        return jsonify({'success': True, 'message': f'{username}님 환영합니다!'})
    else:
        return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}), 401


@app.route('/api/auth/logout')
def api_logout():
    session.clear()
    return redirect(url_for('index'))


# --- 음악 등록 및 유튜브 검색 API ---

@app.route('/api/youtube/search')
def api_youtube_search():
    """
    유튜브 실시간 검색 수행 API (검색어 'q' 필요)
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    results = youtube_live_search(query)
    return jsonify(results)


@app.route('/api/songs/register', methods=['POST'])
@login_required
def api_register_song():
    """
    유튜브 검색 결과에서 혹은 유튜브 URL 파싱을 통해 수동으로 음악을 등록하는 API
    """
    data = request.get_json() or {}
    youtube_id = data.get('youtube_id', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    thumbnail_url = data.get('thumbnail_url', '').strip()
    
    # 수동 URL 입력 지원용 (유튜브 주소를 넣었을 때 ID 추출)
    if 'youtube.com' in youtube_id or 'youtu.be' in youtube_id:
        video_id_match = re.search(r'(?:v=|\/v\/|embed\/|youtu\.be\/|\/shorts\/)([^&\n?#]+)', youtube_id)
        if video_id_match:
            youtube_id = video_id_match.group(1)
        else:
            return jsonify({'success': False, 'message': '유효한 유튜브 동영상 주소가 아닙니다.'}), 400
            
    if not youtube_id:
        return jsonify({'success': False, 'message': '유튜브 동영상 ID가 필요합니다.'}), 400
        
    # 만약 직접 유튜브 주소를 넣어 등록하려는 경우, 메타데이터 정보가 채워져 있지 않다면 자체 백엔드에서 유튜브 파싱 시도
    if not title or not thumbnail_url:
        # 유튜브 가짜 검색에 해당 비디오 ID를 직접 넣어 추출 시도
        search_results = youtube_live_search(youtube_id)
        if search_results:
            title = search_results[0]['title']
            description = search_results[0]['description']
            thumbnail_url = search_results[0]['thumbnail']
        else:
            # 수동 직접 등록 기본값 설정
            title = title or f"유튜브 음악 ({youtube_id})"
            thumbnail_url = thumbnail_url or f"https://i.ytimg.com/vi/{youtube_id}/hqdefault.jpg"
            description = description or "수동 등록된 유튜브 음악입니다."

    conn = database.get_db_connection()
    try:
        conn.execute('''
            INSERT INTO songs (youtube_id, title, description, thumbnail_url)
            VALUES (?, ?, ?, ?)
        ''', (youtube_id, title, description, thumbnail_url))
        conn.commit()
        return jsonify({'success': True, 'message': '새로운 음악이 성공적으로 등록되었습니다!', 'youtube_id': youtube_id})
    except sqlite3.IntegrityError:
        # 이미 존재하는 경우 에러가 아니라 바로 해당 곡 상세페이지로 안내하도록 처리
        return jsonify({'success': True, 'message': '이미 등록되어 있는 음악입니다.', 'youtube_id': youtube_id, 'already_exists': True})
    finally:
        conn.close()


# --- SNS 기능 API (댓글, 좋아요, 해시태그) ---

@app.route('/api/songs/<youtube_id>/like', methods=['POST'])
@login_required
def api_toggle_like(youtube_id):
    """
    좋아요 토글 API (이미 눌렀다면 취소, 아니라면 좋아요 등록)
    """
    user_id = session['user_id']
    conn = database.get_db_connection()
    
    # 곡 등록 여부 확인
    song = conn.execute('SELECT 1 FROM songs WHERE youtube_id = ?', (youtube_id,)).fetchone()
    if not song:
        conn.close()
        return jsonify({'success': False, 'message': '존재하지 않는 음악입니다.'}), 404
        
    # 좋아요 여부 확인
    like_exists = conn.execute('''
        SELECT 1 FROM likes WHERE user_id = ? AND youtube_id = ?
    ''', (user_id, youtube_id)).fetchone()
    
    liked = False
    if like_exists:
        # 이미 좋아요 상태면 해제
        conn.execute('DELETE FROM likes WHERE user_id = ? AND youtube_id = ?', (user_id, youtube_id))
        conn.commit()
    else:
        # 없었다면 좋아요 추가
        conn.execute('INSERT INTO likes (user_id, youtube_id) VALUES (?, ?)', (user_id, youtube_id))
        conn.commit()
        liked = True
        
    # 최신 좋아요 개수 재계산
    count = conn.execute('SELECT COUNT(*) FROM likes WHERE youtube_id = ?', (youtube_id,)).fetchone()[0]
    conn.close()
    
    return jsonify({'success': True, 'liked': liked, 'like_count': count})


@app.route('/api/songs/<youtube_id>/comment', methods=['POST'])
@login_required
def api_post_comment(youtube_id):
    """
    댓글 쓰기 API
    남이 내가 좋아요 한 음악에 댓글을 남기면 실시간 알림(푸시 알람)을 생성합니다.
    """
    user_id = session['user_id']
    username = session['username']
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'success': False, 'message': '댓글 내용을 입력해 주세요.'}), 400
        
    conn = database.get_db_connection()
    try:
        # 1. 댓글 저장
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO comments (youtube_id, user_id, content) VALUES (?, ?, ?)
        ''', (youtube_id, user_id, content))
        comment_id = cursor.lastrowid
        conn.commit()
        
        # 2. 곡 정보 가져오기 (알림 메시지 빌드용)
        song_title = conn.execute('SELECT title FROM songs WHERE youtube_id = ?', (youtube_id,)).fetchone()['title']
        
        # 3. 푸시 알림 로직 구현:
        # 이 음악에 좋아요를 한 사용자들을 검색하되, 본인(댓글 단 사람)은 제외합니다.
        liked_users = conn.execute('''
            SELECT user_id FROM likes 
            WHERE youtube_id = ? AND user_id != ?
        ''', (youtube_id, user_id)).fetchall()
        
        # 알림 테이블에 각각 인서트
        for row in liked_users:
            conn.execute('''
                INSERT INTO notifications (user_id, sender_id, youtube_id, comment_id)
                VALUES (?, ?, ?, ?)
            ''', (row['user_id'], user_id, youtube_id, comment_id))
        conn.commit()
        
        return jsonify({
            'success': True, 
            'comment_id': comment_id,
            'username': username,
            'created_at': '방금 전',
            'content': content
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'댓글 작성 중 오류 발생: {e}'}), 500
    finally:
        conn.close()


@app.route('/api/songs/<youtube_id>/hashtag', methods=['POST'])
@login_required
def api_add_hashtag(youtube_id):
    """
    해시태그 자유 추가 API
    """
    user_id = session['user_id']
    data = request.get_json() or {}
    tag = data.get('tag', '').strip().lower()
    
    # '#' 기호가 포함되어 있다면 제거
    tag = tag.replace('#', '')
    
    if not tag:
        return jsonify({'success': False, 'message': '해시태그를 올바르게 입력해 주세요.'}), 400
        
    if len(tag) > 20:
        return jsonify({'success': False, 'message': '해시태그는 20자 이하이어야 합니다.'}), 400
        
    conn = database.get_db_connection()
    try:
        conn.execute('''
            INSERT INTO hashtags (youtube_id, tag, user_id) VALUES (?, ?, ?)
        ''', (youtube_id, tag, user_id))
        conn.commit()
        return jsonify({'success': True, 'tag': tag})
    except sqlite3.IntegrityError:
        # 이미 동일한 태그가 해당 곡에 등록되어 있는 경우
        return jsonify({'success': False, 'message': '이미 추가된 해시태그입니다.'}), 400
    finally:
        conn.close()


@app.route('/api/songs/<youtube_id>/hashtag/delete', methods=['POST'])
@login_required
def api_delete_hashtag(youtube_id):
    """
    본인이 추가한 해시태그 삭제 API
    """
    user_id = session['user_id']
    data = request.get_json() or {}
    tag = data.get('tag', '').strip()
    
    conn = database.get_db_connection()
    # 해시태그 삭제 (본인이 추가했거나 관리자일 때만 삭제 가능)
    if session.get('role') == 'admin':
        result = conn.execute('DELETE FROM hashtags WHERE youtube_id = ? AND tag = ?', (youtube_id, tag))
    else:
        result = conn.execute('DELETE FROM hashtags WHERE youtube_id = ? AND tag = ? AND user_id = ?', (youtube_id, tag, user_id))
    
    conn.commit()
    rows_deleted = result.rowcount
    conn.close()
    
    if rows_deleted > 0:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '해당 해시태그를 삭제할 권한이 없거나 존재하지 않습니다.'}), 403


# --- 알림 API ---

@app.route('/api/notifications')
@login_required
def api_get_notifications():
    """
    실시간 폴링(Polling)을 통해 로그인 유저의 미확인 알림 개수와 리스트를 리턴합니다.
    """
    user_id = session['user_id']
    conn = database.get_db_connection()
    
    # 1. 아직 읽지 않은 최신 알림 목록 가져오기
    unread_rows = conn.execute('''
        SELECT n.*, sender.username as sender_name, s.title as song_title, c.content as comment_content
        FROM notifications n
        JOIN users sender ON n.sender_id = sender.id
        JOIN songs s ON n.youtube_id = s.youtube_id
        JOIN comments c ON n.comment_id = c.id
        WHERE n.user_id = ? AND n.is_read = 0
        ORDER BY n.created_at DESC
    ''', (user_id,)).fetchall()
    
    unread_list = []
    for r in unread_rows:
        unread_list.append({
            'id': r['id'],
            'sender_name': r['sender_name'],
            'youtube_id': r['youtube_id'],
            'song_title': r['song_title'],
            'comment_content': r['comment_content'][:20] + '...' if len(r['comment_content']) > 20 else r['comment_content'],
            'created_at': '방금 전'
        })
        
    conn.close()
    return jsonify({
        'success': True,
        'unread_count': len(unread_list),
        'notifications': unread_list
    })


@app.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def api_mark_notifications_read():
    """
    모든 읽지 않은 알림을 읽음 처리합니다.
    """
    user_id = session['user_id']
    conn = database.get_db_connection()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# --- 관리자 전용 API ---

@app.route('/api/admin/users/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def api_admin_toggle_role(user_id):
    """
    관리자 권한: 일반 유저 <-> 관리자 역할 토글
    """
    # 자기 자신은 토글 불가하게 방어
    if user_id == session['user_id']:
        return jsonify({'success': False, 'message': '자기 자신의 권한은 변경할 수 없습니다.'}), 400
        
    conn = database.get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': '존재하지 않는 회원입니다.'}), 404
        
    new_role = 'admin' if user['role'] == 'user' else 'user'
    conn.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'new_role': new_role, 'message': '회원 등급이 성공적으로 변경되었습니다.'})


@app.route('/api/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def api_admin_delete_user(user_id):
    """
    관리자 권한: 회원 강제 탈퇴 (삭제)
    """
    if user_id == session['user_id']:
        return jsonify({'success': False, 'message': '자기 자신은 탈퇴할 수 없습니다.'}), 400
        
    conn = database.get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '회원이 성공적으로 강제 탈퇴 처리되었습니다.'})


@app.route('/api/admin/songs/<youtube_id>/delete', methods=['POST'])
@login_required
@admin_required
def api_admin_delete_song(youtube_id):
    """
    관리자 권한: 게시글(음악) 강제 삭제
    """
    conn = database.get_db_connection()
    conn.execute('DELETE FROM songs WHERE youtube_id = ?', (youtube_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '음악 정보 및 관련 데이터가 모두 성공적으로 강제 삭제되었습니다.'})


@app.route('/api/admin/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def api_admin_delete_comment(comment_id):
    """
    관리자 권한: 부적절한 댓글 강제 삭제
    """
    conn = database.get_db_connection()
    conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '부적절한 댓글이 삭제되었습니다.'})


# --- 서버 실행 진입점 ---
if __name__ == '__main__':
    # 0.0.0.0 주소 및 5050번 포트로 구동하여 누구나 쉽게 개발 서버에 접속 가능하도록 합니다.
    app.run(debug=True, host='0.0.0.0', port=5050)
