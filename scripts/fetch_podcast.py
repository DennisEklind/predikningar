
import json
import re
import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FEED_URL = "https://feeds.acast.com/public/shows/karlskogabaptist"

# Hämta Acasts RSS-flöde
request = urllib.request.Request(
    FEED_URL,
    headers={"User-Agent": "PodcastArchive/1.0"}
)

with urllib.request.urlopen(request, timeout=60) as response:
    rss_data = response.read()

root = ET.fromstring(rss_data)
channel = root.find("channel")

if channel is None:
    raise RuntimeError("Hittade ingen RSS-kanal.")

episodes = []

for item in channel.findall("item"):
    title = item.findtext("title", default="").strip()
    description = item.findtext("description", default="")
    pub_date = item.findtext("pubDate", default="")
    link = item.findtext("link", default="")

    enclosure = item.find("enclosure")
    audio_url = enclosure.get("url", "") if enclosure is not None else ""

    # Predikantens namn står före <hr> i beskrivningen.
    speaker = html.unescape(description).split("<hr>")[0]
    speaker = re.sub(r"<[^>]*>", "", speaker).strip()

    episodes.append({
        "title": title,
        "speaker": speaker,
        "pubDate": pub_date,
        "date": pub_date[:16],
        "description": description,
        "link": link,
        "audioUrl": audio_url
    })

# Spara filen i repositoryts rotmapp.
output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "count": len(episodes),
    "episodes": episodes
}

Path("episodes.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Sparade {len(episodes)} avsnitt till episodes.json")
