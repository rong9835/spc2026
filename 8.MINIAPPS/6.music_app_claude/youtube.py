"""
youtube.py
----------
유튜브에서 실제 노래를 검색하는 기능입니다.

초보자 설명:
- 보통 유튜브 데이터를 가져오려면 'API 키'를 발급받아야 합니다.
- 여기서는 학습 목적으로, 유튜브 검색 결과 '웹페이지'를 그대로 받아온 뒤
  그 안에 숨어 있는 데이터(JSON)를 뽑아내는 방식을 사용합니다. (API 키 불필요)
- 유튜브 페이지 구조가 바뀌면 동작하지 않을 수 있으니, 학습용으로만 사용하세요.
"""

import re
import json
import requests

# 유튜브가 우리를 '진짜 브라우저'로 인식하도록 보내는 정보입니다.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def search_youtube(query):
    """
    검색어(query)로 유튜브를 검색해 동영상 목록을 돌려줍니다.

    돌려주는 값: 딕셔너리 리스트
        [{ "youtube_id", "title", "description", "thumbnail_url" }, ...]
    실패하면 빈 리스트 [] 를 돌려줍니다.
    """
    url = f"https://www.youtube.com/results?search_query={query}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []

        # 유튜브 페이지 안에는 "ytInitialData = { ... };" 형태로 데이터가 들어 있습니다.
        # 정규식으로 그 중괄호 { } 부분(JSON)만 뽑아냅니다.
        match = re.search(r"var ytInitialData = ({.*?});", response.text)
        if not match:
            return []

        data = json.loads(match.group(1))
        return _extract_videos(data)

    except Exception as error:
        print(f"유튜브 검색 오류: {error}")
        return []


def _extract_videos(data):
    """
    유튜브가 준 거대한 JSON 안에서 동영상 정보만 골라냅니다.
    JSON 구조가 복잡하므로, 단계별로 안전하게 접근합니다.
    """
    videos = []

    try:
        sections = (
            data["contents"]["twoColumnSearchResultsRenderer"]
            ["primaryContents"]["sectionListRenderer"]["contents"]
        )
    except (KeyError, TypeError):
        return []

    for section in sections:
        items = section.get("itemSectionRenderer", {}).get("contents", [])
        for item in items:
            video = item.get("videoRenderer")
            if not video:
                continue

            youtube_id = video.get("videoId")
            title = _get_text(video.get("title"))
            description = _get_description(video)
            thumbnail = _get_thumbnail(video, youtube_id)

            if youtube_id and title:
                videos.append({
                    "youtube_id": youtube_id,
                    "title": title,
                    "description": description,
                    "thumbnail_url": thumbnail,
                })

            # 너무 많이 가져오지 않도록 10개까지만 모읍니다.
            if len(videos) >= 10:
                return videos

    return videos


def _get_text(title_obj):
    """제목처럼 { "runs": [{"text": "..."}] } 형태인 값을 안전하게 문자열로 꺼냅니다."""
    if not title_obj:
        return ""
    runs = title_obj.get("runs", [])
    return "".join(run.get("text", "") for run in runs)


def _get_description(video):
    """동영상 설명문을 꺼냅니다. (위치가 두 군데일 수 있어 둘 다 시도)"""
    snippets = video.get("detailedMetadataSnippets", [])
    if snippets:
        runs = snippets[0].get("snippetText", {}).get("runs", [])
        text = "".join(run.get("text", "") for run in runs)
        if text:
            return text

    runs = video.get("descriptionSnippet", {}).get("runs", [])
    return "".join(run.get("text", "") for run in runs)


def _get_thumbnail(video, youtube_id):
    """썸네일 이미지 주소를 꺼냅니다. 없으면 영상 ID로 기본 썸네일 주소를 만듭니다."""
    thumbs = video.get("thumbnail", {}).get("thumbnails", [])
    if thumbs:
        return thumbs[-1].get("url", "")
    return f"https://i.ytimg.com/vi/{youtube_id}/hqdefault.jpg"


def extract_video_id(text):
    """
    사용자가 유튜브 '주소(URL)'를 직접 붙여넣었을 때, 그 안에서 영상 ID만 뽑아냅니다.
    예) https://www.youtube.com/watch?v=abc123  ->  abc123
        https://youtu.be/abc123                 ->  abc123
    이미 ID만 들어왔으면 그대로 돌려줍니다.
    """
    if "youtube.com" in text or "youtu.be" in text:
        match = re.search(r"(?:v=|/v/|embed/|youtu\.be/|/shorts/)([^&\n?#]+)", text)
        if match:
            return match.group(1)
        return None
    return text
