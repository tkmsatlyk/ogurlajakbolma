import urllib.request

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱 PRO-SELECT 🔱_》
#profile-update-interval: 0
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Sadece Shadow-Level Profesyonel VIP Havuz 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# Sadece ShadowException ayarında, profesyonel içerik üreten "Babalar" listesi
PRO_SOURCES = [
    # 1. ShadowException (Listenin kalbi)
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    
    # 2. vfarid (Cloudflare Worker'ın mucitlerinden)
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    
    # 3. yebekhe (En eski ve en profesyonel toplayıcılardan)
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt",
    
    # 4. mahdibland (Reality protokolünün piri)
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    
    # 5. tbbatbb (Çok stabil ve nadiren patlayan kaynaklar üretir)
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/v2ray/v2ray.txt"
]

def main():
    print("[+] VØRÐR Pro-Select Motoru Başlatıldı...")
    collected_lines = set()
    
    for url in PRO_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                raw_text = response.read().decode('utf-8', errors='ignore')
                for line in raw_text.splitlines():
                    clean = line.strip()
                    # Sadece link formunda olanları al, açıklamaları ve çöpü at
                    if "://" in clean and not clean.startswith("#") and not clean.startswith("//"):
                        collected_lines.add(clean)
        except:
            continue

    # 1'den başlayarak profesyonel bir şekilde numaralandır
    sorted_links = sorted(list(collected_lines))

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for i, link in enumerate(sorted_links, 1):
            # Her linke profesyonel bir isim etiketi ekle
            if "#" in link:
                new_link = link.split("#")[0] + f"#{i}. VORDR PRO"
            else:
                new_link = link + f"#{i}. VORDR PRO"
            f.write(new_link + "\n")
            
    print("[+] Liste başarıyla profesyonellerden çekildi ve numaralandırıldı.")

if __name__ == "__main__":
    main()
