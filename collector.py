import urllib.request
import re

# 1. ADIM: Senin o asla silinmeyecek özel imzan
HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Canli ve Hızlı VIP Havuz 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# En taze linklerin aktığı ana küresel havuzlar
RAW_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/wuyuncuo/Compiled-Sub/main/v2ray.txt",
    "https://raw.githubusercontent.com/asfytw/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    "https://raw.githubusercontent.com/Zu6666/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt"
]

def main():
    print("[+] VIP Esnek Motor baslatildi...")
    all_raw_text = ""
    
    # Tüm kaynakları indir
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                all_raw_text += response.read().decode('utf-8', errors='ignore') + "\n"
        except Exception as e:
            print(f"[-] Kaynak okunamadi: {url} -> {e}")

    # Protokolleri yakalayan en geniş Regex formülü
    pattern = r'(vless|vmess|trojan|ss|ssr|hysteria|tuic):\/\/[^\s"\'<>]+'
    extracted_links = re.findall(pattern, all_raw_text, re.IGNORECASE)
    
    # Mükerrer olanları sil
    unique_links = list(set(extracted_links))
    
    # Sansürü delme şansı en yüksek olan garanti portlar
    allowed_ports = [":443", ":80"]
    
    final_links = []
    for link in unique_links:
        # Linkin içinde :443 veya :80 portu var mı diye bakar
        if any(port in link for port in allowed_ports):
            # Portun arkasından başka rakam gelmediğini doğrula (Örn: :4433'ü eler)
            port_match = re.search(r':([0-9]+)', link)
            if port_match:
                detected_port = ":" + port_match.group(1)
                if detected_port in allowed_ports:
                    final_links.append(link)

    print(f"[+] Toplam {len(final_links)} adet filtrelenmiş link listeye yazılıyor.")

    # Dosyayı sıfırla ve üzerine mühürle
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for link in final_links:
            f.write(link + "\n")
            
    print("[+] 'toplanan_linkler.txt' basariyla yenilendi!")

if __name__ == "__main__":
    main()
