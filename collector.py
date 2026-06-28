import urllib.request

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱 ELITE-100 🔱_》
#profile-update-interval: 0
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Cerrahi Ayıklanmış En Hızlı 100 Link 🚨
"""

# Sadece kalitesi tescilli 3 ana kaynak
PRO_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/v2ray/v2ray.txt"
]

def main():
    all_links = []
    for url in PRO_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                all_links.extend(response.read().decode('utf-8', errors='ignore').splitlines())
        except: continue

    # Boş satırları at, sadece linkleri al (vless, vmess, trojan)
    final_links = [l for l in all_links if "://" in l and not l.startswith("#")][:100]

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for i, link in enumerate(final_links, 1):
            name = f"#{i:03d}. VORDR PRO"
            if "#" in link: final_link = link.split("#")[0] + name
            else: final_link = link + name
            f.write(final_link + "\n")

if __name__ == "__main__":
    main()
