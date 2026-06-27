import urllib.request
import re

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Sadece Zırhlı Cloudflare VIP Havuzu 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# Sadece arkasında Cloudflare altyapısı barındıran temiz kaynaklar
RAW_SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt",
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat"
]

def main():
    print("[+] VØRÐR Zırhlı Motor Başlatıldı...")
    all_raw_text = ""
    
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                all_raw_text += response.read().decode('utf-8', errors='ignore') + "\n"
        except:
            continue

    pattern = r'(vless|vmess|trojan|ss|ssr|hysteria|tuic)://[^\s"\'<>]+'
    extracted_links = re.findall(pattern, all_raw_text, re.IGNORECASE)
    unique_links = list(set(extracted_links))
    
    final_links = []
    
    # Türkmenistan Wi-Fi'ında delme ihtimali en yüksek kelimeleri arıyoruz
    # İçinde 'worker', 'cloudflare', 'pages', 'dev' veya port olarak '443' geçen zırhlıları seçiyoruz
    for link in unique_links:
        link_lower = link.lower()
        if "worker" in link_lower or "cloudflare" in link_lower or "pages.dev" in link_lower or "trycloudflare" in link_lower or ":443" in link_lower:
            final_links.append(link)

    print(f"[+] Çöpler elendi. Elde kalan {len(final_links)} adet zırhlı Cloudflare linki yazılıyor.")

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for link in final_links:
            f.write(link + "\n")
            
    print("[+] 'toplanan_linkler.txt' elmas linklerle güncellendi!")

if __name__ == "__main__":
    main()
