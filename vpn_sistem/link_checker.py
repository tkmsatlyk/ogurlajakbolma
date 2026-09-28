#!/usr/bin/env python3
import base64, hashlib, json, math, os, queue, random, shutil, socket
import subprocess, tempfile, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs, unquote

FILE = "toplanan_linkler.txt"
XRAY = os.environ.get("XRAY_BIN", "xray")
TEST_URL = "https://www.gstatic.com/generate_204"
INTERVAL = 15 * 60
MAX_MS = 3000
WORKERS = 30
REQ_TIMEOUT = 8
BASE_PORT = 20000

SIM = False
SIM_MEDIAN = 0.45
SIM_SIGMA = 0.6
SIM_SPIKE = 0.08
BLOCK_SECURE = 0.08
BLOCK_PLAIN = 0.40
BLOCK_ODD_PORT = 0.05
GOOD_PORTS = {443, 8443, 2053, 2083, 2087, 2096}
PEAK_HOURS = range(19, 24)
NIGHT_HOURS = range(2, 7)

STATS = Counter()
ERRS = []
PORTS = queue.Queue()
for _p in range(BASE_PORT, BASE_PORT + WORKERS):
    PORTS.put(_p)


def b64(s):
    s = s.strip()
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_stream(p):
    net = {"tcp": "tcp", "raw": "tcp", "ws": "ws", "grpc": "grpc",
           "httpupgrade": "httpupgrade", "xhttp": "xhttp",
           "splithttp": "xhttp"}.get(p["net"])
    if net is None:
        raise ValueError("desteklenmeyen tasima")
    s = {"network": net}
    host, path = p["host"], p["path"]
    if net == "ws":
        s["wsSettings"] = {"path": path or "/"}
        if host:
            s["wsSettings"]["headers"] = {"Host": host}
    elif net == "grpc":
        s["grpcSettings"] = {"serviceName": p.get("service") or path}
    elif net == "httpupgrade":
        s["httpupgradeSettings"] = {"path": path or "/", "host": host}
    elif net == "xhttp":
        s["xhttpSettings"] = {"path": path or "/", "host": host,
                              "mode": p.get("mode") or "auto"}
    elif net == "tcp" and p.get("header") == "http":
        s["tcpSettings"] = {"header": {"type": "http", "request": {
            "path": [path or "/"], "headers": {"Host": [host] if host else []}}}}
    sec = p["sec"]
    if sec == "tls":
        s["security"] = "tls"
        t = {"serverName": p["sni"] or host or p["addr"],
             "fingerprint": p["fp"] or "chrome"}
        if p["alpn"]:
            t["alpn"] = p["alpn"].split(",")
        if p["insecure"]:
            t["allowInsecure"] = True
        s["tlsSettings"] = t
    elif sec == "reality":
        s["security"] = "reality"
        s["realitySettings"] = {"serverName": p["sni"], "fingerprint": p["fp"] or "chrome",
                                "publicKey": p["pbk"], "shortId": p["sid"],
                                "spiderX": p["spx"] or "/"}
    return s


def build(link):
    link = link.strip()
    scheme = link.split("://", 1)[0].lower()
    if scheme == "vmess":
        d = json.loads(b64(link[8:]))
        p = {"net": (d.get("net") or "tcp").lower(), "sec": "tls" if d.get("tls") == "tls" else "none",
             "host": d.get("host", ""), "path": d.get("path", ""), "sni": d.get("sni", ""),
             "fp": d.get("fp", ""), "alpn": d.get("alpn", ""), "service": d.get("path", ""),
             "header": d.get("type", "none"), "insecure": False, "addr": d["add"]}
        port = int(d["port"])
        out = {"protocol": "vmess", "settings": {"vnext": [{"address": d["add"], "port": port,
               "users": [{"id": d["id"], "alterId": int(d.get("aid") or 0),
                          "security": d.get("scy") or "auto"}]}]},
               "streamSettings": make_stream(p)}
        return out, d["add"], port, p["sec"] != "none"

    if scheme in ("vless", "trojan"):
        u = urlparse(link)
        qs = parse_qs(u.query)

        def g(k, dv=""):
            return unquote(qs.get(k, [dv])[0])
        sec = g("security", "tls" if scheme == "trojan" else "none").lower()
        p = {"net": g("type", "tcp").lower(), "sec": sec, "host": g("host"), "path": g("path"),
             "sni": g("sni") or g("peer"), "fp": g("fp"), "alpn": g("alpn"), "pbk": g("pbk"),
             "sid": g("sid"), "spx": g("spx"), "service": g("serviceName"),
             "header": g("headerType", "none"), "mode": g("mode"),
             "insecure": g("allowInsecure") == "1" or g("insecure") == "1", "addr": u.hostname}
        user = unquote(u.username or "")
        if scheme == "vless":
            usr = {"id": user, "encryption": g("encryption", "none") or "none"}
            if g("flow"):
                usr["flow"] = g("flow")
            out = {"protocol": "vless", "settings": {"vnext": [{"address": u.hostname,
                   "port": u.port, "users": [usr]}]}, "streamSettings": make_stream(p)}
        else:
            out = {"protocol": "trojan", "settings": {"servers": [{"address": u.hostname,
                   "port": u.port, "password": user}]}, "streamSettings": make_stream(p)}
        return out, u.hostname, u.port, sec != "none"

    if scheme == "ss":
        body = link[5:].split("#")[0]
        q = ""
        if "?" in body:
            body, q = body.split("?", 1)
        if "plugin" in q:
            raise ValueError("plugin")
        if "@" not in body:
            body = b64(body).decode()
        userinfo, _, hostport = body.rpartition("@")
        if ":" not in userinfo:
            userinfo = b64(userinfo).decode()
        method, _, password = userinfo.partition(":")
        host, _, port = hostport.rpartition(":")
        host = host.strip("[]")
        port = int(port.strip("/"))
        out = {"protocol": "shadowsocks", "settings": {"servers": [{"address": host,
               "port": port, "method": method, "password": password}]}}
        return out, host, port, False

    raise ValueError("desteklenmeyen protokol")


def real_test(out, port):
    cfg = {"log": {"loglevel": "none"},
           "inbounds": [{"listen": "127.0.0.1", "port": port, "protocol": "socks",
                         "settings": {"auth": "noauth", "udp": False}}],
           "outbounds": [out]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(cfg, f)
        path = f.name
    proc = subprocess.Popen([XRAY, "run", "-c", path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(40):
            if proc.poll() is not None:
                STATS["xray_acilmadi"] += 1
                if len(ERRS) < 3:
                    ERRS.append(proc.stderr.read().decode("utf-8", "ignore")[:300])
                return None
            try:
                socket.create_connection(("127.0.0.1", port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            STATS["xray_port_yok"] += 1
            return None
        times = []
        for _ in range(2):
            t0 = time.time()
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-x", f"socks5h://127.0.0.1:{port}",
                                "--max-time", str(REQ_TIMEOUT), "-w", "%{http_code}", TEST_URL],
                               capture_output=True, text=True)
            if r.stdout.strip() != "204":
                if not times:
                    STATS[f"baglanti_yok_curl{r.returncode}"] += 1
                    return None
                continue
            times.append(int((time.time() - t0) * 1000))
        return min(times) if times else None
    finally:
        proc.kill()
        proc.wait()
        os.unlink(path)


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


def sim_delay():
    d = random.lognormvariate(math.log(SIM_MEDIAN), SIM_SIGMA) * load_factor()
    if random.random() < SIM_SPIKE:
        d += random.uniform(1.5, 3.0)
    return int(d * 1000)


def check(link):
    try:
        out, host, port, secure = build(link)
    except Exception:
        STATS["desteklenmeyen_veya_bozuk"] += 1
        return link, None
    if SIM and blocked(host, port, secure):
        STATS["simulasyon_engel"] += 1
        return link, None
    lp = PORTS.get()
    try:
        ms = real_test(out, lp)
    except Exception as e:
        STATS["hata"] += 1
        if len(ERRS) < 3:
            ERRS.append(str(e)[:200])
        ms = None
    finally:
        PORTS.put(lp)
    if ms is None:
        return link, None
    if SIM:
        ms += sim_delay()
    if ms > MAX_MS:
        STATS["cok_yavas"] += 1
        return link, None
    STATS["calisiyor"] += 1
    return link, ms


def run_once():
    with open(FILE, encoding="utf-8") as f:
        links = list(dict.fromkeys(l.strip() for l in f if "://" in l))
    shutil.copy(FILE, FILE + ".bak")
    STATS.clear()
    ERRS.clear()
    with ThreadPoolExecutor(WORKERS) as ex:
        results = list(ex.map(check, links))
    alive = sorted((r for r in results if r[1] is not None), key=lambda r: r[1])
    with open(FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l, _ in alive) + "\n")
    print(f"{time.strftime('%H:%M:%S')} - {len(alive)}/{len(links)} calisiyor, "
          f"{len(links) - len(alive)} silindi")
    print("Ayrinti:", dict(STATS))
    for e in ERRS:
        print("Hata ornegi:", e)


if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(INTERVAL)
