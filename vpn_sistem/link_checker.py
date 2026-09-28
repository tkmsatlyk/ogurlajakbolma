#!/usr/bin/env python3
import base64, hashlib, json, math, random, shutil, socket, time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

FILE = "toplanan_linkler.txt"
INTERVAL = 15 * 60
TIMEOUT = 5
ATTEMPTS = 3
WORKERS = 100
MAX_MS = 3000

SIM = True
UDP_SCHEMES = {"hysteria2", "hy2", "hysteria", "tuic"}

BASE_LATENCY = 0.45
LATENCY_SIGMA = 0.6
SPIKE_CHANCE = 0.05
SPIKE_RANGE = (1.5, 3.0)
RESET_CHANCE = 0.04
LOSS_GOOD = 0.05
LOSS_BAD = 0.60
P_GOOD_TO_BAD = 0.15
P_BAD_TO_GOOD = 0.30
BLOCK_SECURE = 0.10
BLOCK_PLAIN = 0.40
BLOCK_ODD_PORT = 0.10
GOOD_PORTS = {443, 8443, 2053, 2083, 2087, 2096}
PEAK_HOURS = range(19, 24)
NIGHT_HOURS = range(2, 7)


def b64(s):
    s = s.strip()
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def parse(link):
    scheme = link.split("://", 1)[0].lower()
    if scheme == "vmess":
        d = json.loads(b64(link[8:]))
        return scheme, d["add"], int(d["port"]), d.get("tls") == "tls"
    if scheme == "ss":
        body = link[5:].split("#")[0]
        if "@" not in body:
            body = b64(body).decode()
        u = urlparse("ss://" + body)
        return scheme, u.hostname, u.port, False
    u = urlparse(link)
    text = link.lower()
    secure = (scheme == "trojan" or "security=tls" in text
              or "security=reality" in text)
    return scheme, u.hostname, u.port, secure


def load_factor():
    hour = (time.gmtime().tm_hour + 5) % 24
    if hour in PEAK_HOURS:
        return 1.5
    if hour in NIGHT_HOURS:
        return 0.8
    return 1.0


def blocked(host, port, secure):
    p = BLOCK_SECURE if secure else BLOCK_PLAIN
    if port not in GOOD_PORTS:
        p += BLOCK_ODD_PORT
    h = int(hashlib.sha256(f"{host}:{port}".encode()).hexdigest()[:8], 16)
    return (h / 0xFFFFFFFF) < p


def probe(host, port, secure):
    load = 1.0
    bad = False
    if SIM:
        if blocked(host, port, secure):
            time.sleep(1)
            return None
        load = load_factor()
    for _ in range(ATTEMPTS):
        t0 = time.time()
        if SIM:
            if bad:
                bad = random.random() >= P_BAD_TO_GOOD
            else:
                bad = random.random() < P_GOOD_TO_BAD
            loss = min(0.95, (LOSS_BAD if bad else LOSS_GOOD) * load)
            if random.random() < RESET_CHANCE:
                time.sleep(0.2)
                continue
            if random.random() < loss:
                time.sleep(TIMEOUT)
                continue
            delay = random.lognormvariate(math.log(BASE_LATENCY), LATENCY_SIGMA) * load
            if random.random() < SPIKE_CHANCE:
                delay += random.uniform(*SPIKE_RANGE)
            time.sleep(delay)
        try:
            socket.create_connection((host, port), TIMEOUT).close()
        except OSError:
            continue
        ms = int((time.time() - t0) * 1000)
        if ms <= MAX_MS:
            return ms
    return None


def check(link):
    try:
        scheme, host, port, secure = parse(link)
        if scheme in UDP_SCHEMES:
            return link, MAX_MS
        return link, probe(host, port, secure)
    except Exception:
        return link, None


def run_once():
    with open(FILE, encoding="utf-8") as f:
        links = list(dict.fromkeys(l.strip() for l in f if "://" in l))
    shutil.copy(FILE, FILE + ".bak")
    with ThreadPoolExecutor(WORKERS) as ex:
        results = list(ex.map(check, links))
    alive = sorted((r for r in results if r[1] is not None and r[1] <= MAX_MS),
                   key=lambda r: r[1])
    with open(FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l, _ in alive) + "\n")
    print(f"{time.strftime('%H:%M:%S')} - {len(alive)}/{len(links)} calisiyor, "
          f"{len(links) - len(alive)} silindi")


if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(INTERVAL)
