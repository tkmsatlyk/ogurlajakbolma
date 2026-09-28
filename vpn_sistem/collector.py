#!/usr/bin/env python3
import html, re, urllib.request

FILE = "toplanan_linkler.txt"
CHANNELS = ["LonUp_M", "v2raysvmess"]
PAGES = 5

LINK_RE = re.compile(r"(?:vmess|vless|trojan|ss|hysteria2|hy2|tuic)://[^\s<>\"']+")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")


def scrape(channel):
    found, before = [], None
    for _ in range(PAGES):
        url = f"https://t.me/s/{channel}" + (f"?before={before}" if before else "")
        try:
            page = get(url)
        except Exception as e:
            print(f"{channel}: hata {e}")
            break
        found += LINK_RE.findall(html.unescape(page))
        ids = [int(i) for i in re.findall(rf'data-post="{channel}/(\d+)"', page)]
        if not ids:
            break
        before = min(ids)
    return found


def collect():
    try:
        with open(FILE, encoding="utf-8") as f:
            old = {l.strip() for l in f if "://" in l}
    except FileNotFoundError:
        old = set()
    new = set()
    for ch in CHANNELS:
        new |= {l.rstrip(".,;)") for l in scrape(ch)}
    added = new - old
    with open(FILE, "a", encoding="utf-8") as f:
        for l in sorted(added):
            f.write(l + "\n")
    print(f"{len(added)} yeni link eklendi (toplam {len(old | new)})")


if __name__ == "__main__":
    collect()
