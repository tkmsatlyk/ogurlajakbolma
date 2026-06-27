import urllib.request

# 1. ADIM: Senin o şanlı imzan
HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Canli ve Sınırsız VIP Havuz 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# O büyük abonelik sahiplerinin beslendiği EN BÜYÜK ana GitHub havuzları
RAW_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/wuyuncuo/Compiled-Sub/main/v2ray.txt",
    "https://raw.githubusercontent.com/asfytw/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    "https://raw.githubusercontent.com/Zu6666/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"
]

def main():
    print("[+] Garanti satır motoru başlatıldı...")
    final_links = []
    
    # Tüm kaynaklardan verileri indir ve satır satır oku
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                lines = response.read().decode('utf-8', errors='ignore').splitlines()
                
                for line in lines:
                    clean_line = line.strip()
                    # Satırın içinde vless://, vmess:// veya genel olarak :// varsa ve boş değilse al
                    if "://" in clean_line and not clean_line.startswith("#"):
                        final_links.append(clean_line)
        except Exception as e:
            print(f"[-] Kaynak çekilemedi: {url}")

    # Aynı olan (mükerrer) linkleri temizle
    unique_links = list(set(final_links))

    print(f"[+] Filtresiz tam {len(unique_links)} adet GERÇEK LİNK listeye yazılıyor!")

    # Dosyayı sıfırla, başlığı mühürle ve TÜM linkleri doğrudan bas
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for link in unique_links:
            f.write(link + "\n")
            
    print("[+] 'toplanan_linkler.txt' binlerce gerçek linkle dolduruldu!")

if __name__ == "__main__":
    main()
