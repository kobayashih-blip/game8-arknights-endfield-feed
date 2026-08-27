#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from html import unescape
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET

SOURCE = "https://game8.jp/arknights-endfield/search?q="
SITE = "https://game8.jp"
OUTPUT = Path(__file__).parent / "docs" / "feed.xml"
JST = timezone(timedelta(hours=9))


def clean(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value)).strip()


def extract(block: str, class_name: str) -> str:
    match = re.search(
        rf'<p class="{re.escape(class_name)}">(.*?)</p>', block, re.DOTALL
    )
    return clean(match.group(1)) if match else ""


request = urllib.request.Request(
    SOURCE, headers={"User-Agent": "Mozilla/5.0 (compatible; personal RSS feed)"}
)
with urllib.request.urlopen(request, timeout=30) as response:
    page = response.read().decode("utf-8")

list_match = re.search(
    r'<ul class="c-archiveSearchList">(.*?)</ul>', page, re.DOTALL
)
if not list_match:
    raise RuntimeError("Game8の記事一覧を検出できませんでした")

items = []
for block in re.findall(
    r'<li class="c-archiveSearchListItem">.*?</li>', list_match.group(1), re.DOTALL
):
    link_match = re.search(r'href="(/arknights-endfield/\d+)"', block)
    title = extract(block, "c-archiveSearchListItem__title")
    description = extract(block, "c-archiveSearchListItem__description")
    date_text = re.sub(
        r"\s+", " ", extract(block, "c-archiveSearchListItem__date")
    )
    if not link_match or not title or not date_text:
        continue
    updated = datetime.strptime(date_text, "%Y.%m.%d %H:%M").replace(tzinfo=JST)
    items.append(
        {
            "title": title,
            "description": description,
            "link": SITE + link_match.group(1),
            "updated": updated,
        }
    )

items.sort(key=lambda item: item["updated"], reverse=True)
ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
rss = ET.Element("rss", {"version": "2.0"})
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "Game8 アークナイツ：エンドフィールド 更新情報"
ET.SubElement(channel, "link").text = SOURCE
ET.SubElement(channel, "description").text = (
    "Game8『アークナイツ：エンドフィールド』の記事を最終更新日時順で配信"
)
ET.SubElement(channel, "language").text = "ja"
ET.SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
ET.SubElement(channel, "ttl").text = "30"

for entry in items:
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = entry["title"]
    ET.SubElement(item, "link").text = entry["link"]
    ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = entry["link"]
    ET.SubElement(item, "pubDate").text = format_datetime(entry["updated"])
    ET.SubElement(item, "description").text = entry["description"]

ET.indent(rss, space="  ")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
ET.ElementTree(rss).write(OUTPUT, encoding="utf-8", xml_declaration=True)
print(f"Generated {OUTPUT} with {len(items)} items")
