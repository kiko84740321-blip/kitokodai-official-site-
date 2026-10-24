
import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

API_KEY = os.environ["YOUTUBE_API_KEY"]
BASE_URL = "https://www.googleapis.com/youtube/v3/"

def get_json(endpoint, params):
    params["key"] = API_KEY
    url = BASE_URL + endpoint + "?" + urlencode(params)
    with urlopen(url, timeout=30) as response:
        return json.load(response)

# チャンネルのアップロード動画一覧を取得
channel = get_json("channels", {
    "part": "contentDetails",
    "forHandle": "@kitokodai"
})

items = channel.get("items", [])
if not items:
    raise RuntimeError("YouTubeチャンネルが見つかりません")

uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

videos_data = get_json("playlistItems", {
    "part": "snippet",
    "playlistId": uploads_id,
    "maxResults": 3
})

videos = []

for item in videos_data.get("items", []):
    snippet = item["snippet"]
    video_id = snippet["resourceId"]["videoId"]
    thumbnails = snippet.get("thumbnails", {})

    thumbnail = (
        thumbnails.get("high")
        or thumbnails.get("medium")
        or thumbnails.get("default")
        or {}
    ).get("url", "")

    videos.append({
        "id": video_id,
        "title": snippet["title"],
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail": thumbnail,
        "published": snippet.get("publishedAt", "")
    })

with open("videos.json", "w", encoding="utf-8") as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)

print(f"{len(videos)}本の動画をvideos.jsonに保存しました")
