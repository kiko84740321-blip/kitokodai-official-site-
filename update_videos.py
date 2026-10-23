import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime

API_KEY = os.environ["YOUTUBE_API_KEY"]
HANDLE = "@kitokodai"

BASE = "https://www.googleapis.com/youtube/v3"


def api_get(endpoint, params):
    params["key"] = API_KEY
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def duration_seconds(value):
    # YouTubeのISO 8601形式（例: PT3M25S）を秒に変換
    match = re.fullmatch(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        value
    )

    if not match:
        return 0

    hours, minutes, seconds = (
        int(part or 0) for part in match.groups()
    )

    return hours * 3600 + minutes * 60 + seconds


def main():
    channel = api_get("channels", {
        "part": "contentDetails",
        "forHandle": HANDLE,
    })

    items = channel.get("items", [])

    if not items:
        raise RuntimeError(
            "YouTubeチャンネルが見つかりませんでした。HANDLEを確認してください。"
        )

    uploads_id = (
        items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    )

    # チャンネルの最新投稿を最大50件取得
    playlist = api_get("playlistItems", {
        "part": "snippet,contentDetails",
        "playlistId": uploads_id,
        "maxResults": 50,
    })

    uploaded = playlist.get("items", [])

    video_ids = [
        item["contentDetails"]["videoId"]
        for item in uploaded
        if item.get("contentDetails", {}).get("videoId")
    ]

    if not video_ids:
        raise RuntimeError("動画が見つかりませんでした。")

    details = api_get("videos", {
        "part": "snippet,contentDetails",
        "id": ",".join(video_ids),
    })

    videos_by_id = {
        video["id"]: video
        for video in details.get("items", [])
    }

    # タイトルにこれらの語がある動画は除外
    short_markers = [
        "#shorts",
        "#short",
        "shorts",
        "ショート動画",
        "ショート",
    ]

    results = []

    # 投稿一覧の新しい順に判定
    for item in uploaded:
        video_id = item["contentDetails"]["videoId"]
        video = videos_by_id.get(video_id)

        if not video:
            continue

        snippet = video["snippet"]
        title = snippet["title"]
        title_lower = title.lower()

        # Shortsらしいタイトルを除外
        if any(marker in title_lower for marker in short_markers):
            continue

        seconds = duration_seconds(
            video["contentDetails"]["duration"]
        )

        # 60秒以下は除外
        if seconds <= 60:
            continue

        thumbnails = snippet.get("thumbnails", {})
        thumbnail = (
            thumbnails.get("maxres")
            or thumbnails.get("high")
            or thumbnails.get("medium")
            or thumbnails.get("default")
        )

        if not thumbnail:
            continue

        results.append({
            "id": video_id,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail": thumbnail["url"],
            "published": snippet["publishedAt"],
        })

        if len(results) == 3:
            break

    with open("videos.json", "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"videos.jsonを更新しました：{len(results)}件")


if __name__ == "__main__":
    main()
