import urllib.request
import re

# 1. ADIM: Senin o şanlı imzan
HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Telegram & GitHub VIP Canli Havuz 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# EN AKTİF GİTHUB HAVUZLARI
GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/wuyuncuo/Compiled-Sub/main/v2ray.txt",
    "https://raw.githubusercontent.com/asfytw/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    "https://raw.githubusercontent.com/Zu6666/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"
]

# 7/24 TAZE LİNK AKAN TELEGRAM KANALLARI (API anahtarsız gizli kazıma yöntemi)
TELEGRAM_CHANNELS = [
    "https://t.me/s/v2rayng_org",
    "https://t.me/s/v2rayng_vpn",
    "https://t.me/s/FreeVlessVpn",
    "https://t.me/s/V2rayNG_VPNN",
    "https://t.me/s/v2ray_outlineee",
    "https://t.me/s/vmess_vless_v2ray",
    "https://t.me/s/Shadowsocks_v2ray"
]

def main():
    print("[+] VØRÐR Hibrit Motor Başlatıldı...")
    collected_lines = []
    
    # --- GİTHUB KAYNAKLARINI SÖMÜR ---
    for url in GITHUB_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as response:
                lines = response.read().decode('utf-8', errors='ignore').splitlines()
                for line in lines:
                    clean = line.strip()
                    if "://" in clean and not clean.startswith("#") and len(clean) > 15:
                        collected_lines.append(clean)
        except:
            continue

    # --- TELEGRAM KANALLARINI KAZI ---
    # Telegram kanallarının son mesajlarını tarayıp içindeki linkleri cımbızla çeker
    for url in TELEGRAM_CHANNELS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=12) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                
                # HTML kodunun içinden protokolleri eksiksiz yakalayan Regex
                pattern = r'(vless|vmess|trojan|ss|ssr|hysteria|tuic):\/\/[^\s"\'<>\n\r\t]+'
                links = re.findall(pattern, html_content, re.IGNORECASE)
                for link in links:
                    if len(link) > 15:
                        collected_lines.append(link)
        except:
            continue

    # --- AYNI OLANLARI SİL VE TEMİZLE ---
    unique_links = list(set(collected_lines))
    print(f"[+] Toplam {len(unique_links)} adet eşsiz link havuzda birleştirildi.")

    # --- DOSYAYA YAZ ---
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for link in unique_links:
            f.write(link + "\n")
            
    print("[+] 'toplanan_linkler.txt' başarıyla güncellendi!")

if __name__ == "__main__":
    main()
