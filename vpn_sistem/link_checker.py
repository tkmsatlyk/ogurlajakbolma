#!/usr/bin/env python3
import base64, json, random, shutil, socket, time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

FILE = "toplanan_linkler.txt"
INTERVAL = 15 * 60
TIMEOUT = 5
ATTEMPTS = 3
WORKERS = 100

SIM = True
SIM_DELAY = (0.3, 1.5)
SIM_LOSS = 0.25
UDP_SCHEMES = {"hysteria2", "hy2", "hysteria", "tuic"}


def b64(s):
    s = s.strip()
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def parse(link):
    scheme = link.split("://", 1)[0].lower()
    if scheme == "vmess":
        d = json.loads(b64(link[8:]))
        return scheme, d["add"], int(d["port"])
    if scheme == "ss":
        body = link[5:].split("#")[0]
        if "@" not in body:
            body = b64(body).decode()
        u = urlparse("ss://" + body)
        return scheme, u.hostname, u.port
    u = urlparse(link)
    return scheme, u.hostname, u.port


def probe(host, port):
    for _ in range(ATTEMPTS):
        t0 = time.time()
        if SIM:
            time.sleep(random.uniform(*SIM_DELAY))
            if random.random() < SIM_LOSS:
                time.sleep(TIMEOUT)
                continue
        try:
            socket.create_connection((host, port), TIMEOUT).close()
            return int((time.time() - t0) * 1000)
        except OSError:
            pass
    return None


def check(link):
    try:
        scheme, host, port = parse(link)
        if scheme in UDP_SCHEMES:
            return link, 99999
        return link, probe(host, port)
    except Exception:
        return link, None


def run_once():
    with open(FILE, encoding="utf-8") as f:
        links = list(dict.fromkeys(l.strip() for l in f if "://" in l))
    shutil.copy(FILE, FILE + ".bak")
    with ThreadPoolExecutor(WORKERS) as ex:
        results = list(ex.map(check, links))
    alive = sorted((r for r in results if r[1] is not None), key=lambda r: r[1])
    with open(FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l, _ in alive) + "\n")
    print(f"{time.strftime('%H:%M:%S')} - {len(alive)}/{len(links)} calisiyor, "
          f"{len(links) - len(alive)} silindi")


if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(INTERVAL)
