import urllib.request

# Senin şanlı markan ve sonsuz abonelik ayarları
HEADER = """#profile-title: 《_🜲 VØRÐR 🔱 MASTER 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Cerrahi Elemeli VIP Havuz (Max 1500) 🚨
#subscription-userinfo: upload=0; download=0; total=1073741824000; expire=1924992000
"""

PRO_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/v2ray/v2ray.txt"
]

def main():
    collected_links = set() # Set kullanarak kopyaları otomatik yok ediyoruz
    
    for url in PRO_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    if "://" in line and not line.startswith("#"):
                        collected_links.add(line.strip())
        except: continue

    # Kopyaları sildik, şimdi listeyi 1500 ile sınırla
    final_list = list(collected_links)[:1500]

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for i, link in enumerate(final_list, 1):
            # İsimlendirme: Link + #Sıra Numarası + 《_🜲 VØRÐR 🔱_》
            name = f"#{i:04d}. 《_🜲 VØRÐR 🔱_》"
            if "#" in link:
                clean_link = link.split("#")[0] + name
            else:
                clean_link = link + name
            f.write(clean_link + "\n")

if __name__ == "__main__":
    main()
