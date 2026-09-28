#!/usr/bin/env python3
import html, re, time, urllib.request

FILE = "toplanan_linkler.txt"
CHANNELS = ["LonUp_M", "v2raysvmess"]
LIMIT = 300
MAX_PAGES = 60

LINK_RE = re.compile(r"(?:vmess|vless|trojan|ss|hysteria2|hy2|tuic)://[^\s<>\"']+")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")


def scrape(channel):
    found, seen, before = [], set(), None
    for _ in range(MAX_PAGES):
        url = f"https://t.me/s/{channel}" + (f"?before={before}" if before else "")
        try:
            page = get(url)
        except Exception as e:
            print(f"{channel}: hata {e}")
            break
        links = LINK_RE.findall(html.unescape(page))
        for l in reversed(links):
            l = l.rstrip(".,;)")
            if l not in seen:
                seen.add(l)
                found.append(l)
        if len(found) >= LIMIT:
            break
        ids = [int(i) for i in re.findall(rf'data-post="{channel}/(\d+)"', page)]
        if not ids:
            break
        before = min(ids)
        time.sleep(1)
    return found[:LIMIT]


def collect():
    new = []
    for ch in CHANNELS:
        for l in scrape(ch):
            if l not in new:
                new.append(l)
    if not new:
        print("Yeni link bulunamadi, eski liste korundu")
        return
    with open(FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new) + "\n")
    print(f"{len(new)} yeni link yazildi, eski liste silindi")


if __name__ == "__main__":
    collect()
