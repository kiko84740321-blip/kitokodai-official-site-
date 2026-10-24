
import json
import re
import time
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from html.parser import HTMLParser

SOURCE_URL = "https://www.tunecore.co.jp/artists/Kodai-Kito"

def get_html(url):
    req = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")

# TuneCoreのHTMLを解析するためのライブラリを使用
try:
    from bs4 import BeautifulSoup
except ImportError:
    raise RuntimeError("beautifulsoup4 が必要です")

html = get_html(SOURCE_URL)
soup = BeautifulSoup(html, "html.parser")

def clean_title(text):
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"20\d{2}年?$", "", text).strip()
    text = re.sub(r"^20\d{2}-\d{2}-\d{2}", "", text).strip()
    return text

def get_section_items(section_name, stop_names):
    headings = soup.find_all(
        lambda tag:
            tag.name in ("h1", "h2", "h3", "h4")
            and section_name in tag.get_text(" ", strip=True)
    )

    if not headings:
        raise RuntimeError(
            f"「{section_name}」の見出しが見つかりません"
        )

    items = []
    seen = set()

    for node in headings[0].find_all_next():
        if node.name in ("h1", "h2", "h3", "h4"):
            heading_text = node.get_text(" ", strip=True)
            if any(name in heading_text for name in stop_names):
                break

        if node.name != "a" or not node.get("href"):
            continue

        href = node["href"]
        if "linkco.re/" not in href:
            continue

        title = clean_title(node.get_text(" ", strip=True))
        if not title or href in seen:
            continue

        seen.add(href)
        items.append({
            "title": title,
            "url": href
        })

    return items

albums = get_section_items(
    "アルバム",
    ["シングル", "動画", "アーティスト情報"]
)

singles = get_section_items(
    "シングル",
    ["動画", "アーティスト情報"]
)

def add_artwork(item):
    try:
        html = get_html(item["url"])
        page = BeautifulSoup(html, "html.parser")

        image = page.find(
            "meta",
            property="og:image"
        )

        item["thumbnail"] = (
            image.get("content", "")
            if image else ""
        )
    except Exception:
        item["thumbnail"] = ""

    return item

releases = {
    "albums": [add_artwork(x) for x in albums[:1]],
    "singles": [add_artwork(x) for x in singles[:2]]
}

if not releases["albums"]:
    raise RuntimeError("アルバム情報を取得できませんでした")

if len(releases["singles"]) < 2:
    raise RuntimeError("シングル2曲を取得できませんでした")

with open("releases.json", "w", encoding="utf-8") as f:
    json.dump(releases, f, ensure_ascii=False, indent=2)

print("アルバム1枚・シングル2曲を保存しました")
