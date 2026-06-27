import urllib.request
import re

# 1. ADIM: Senin o asla silinmeyecek özel imzan
HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ tarafından ⚡️ yasalan getir 🪪 bot 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# 2. ADIM: O büyük abonelik sahiplerinin beslendiği ana GitHub havuzları
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
    print("[+] VIP Port toplayıcı motor başlatıldı...")
    all_raw_text = ""
    
    # Tüm kaynaklardan ham verileri indir
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                all_raw_text += response.read().decode('utf-8', errors='ignore') + "\n"
        except Exception as e:
            print(f"[-] Kaynak çekilemedi: {url} -> {e}")

    # Linkleri Regex ile cımbızla çekme
    pattern = r'(vless|vmess|trojan|ss|ssr|hysteria|tuic)://[^\s"\'<>]+'
    extracted_links = re.findall(pattern, all_raw_text, re.IGNORECASE)
    
    # Aynı olan linkleri temizle
    unique_links = list(set(extracted_links))
    
    # O ustaların kullandığı tüm aktif portlar (443, 80 ve Cloudflare portları)
    allowed_ports = [
        ":443", ":80", 
        ":8080", ":8443", ":2052", ":2053", ":2082", ":2083", ":2086", ":2087", ":2095", ":2096",
        ":2097", ":8880", ":10086", ":54321"
    ]
    
    final_links = []
    for link in unique_links:
        # Tam port eşleşmesini kontrol et (arkasından başka sayı gelmeyenleri alır)
        port_match = re.search(r':([0-9]+)', link)
        if port_match:
            detected_port = ":" + port_match.group(1)
            if detected_port in allowed_ports:
                final_links.append(link)

    print(f"[+] Elemanların portlarıyla senkronize {len(final_links)} adet canlı link ayıklandı.")

    # Dosyayı sıfırla, başlığı mühürle ve yeni linkleri yaz
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for link in final_links:
            f.write(link + "\n")
            
    print("[+] 'toplanan_linkler.txt' başarıyla güncellendi!")

if __name__ == "__main__":
    main()
