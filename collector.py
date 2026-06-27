import urllib.request
import re
import socket

# 1. ADIM: Senin o silinmez özel imzan
HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Canli ve Calisan VIP Havuz 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# Ana Kaynak Havuzları
RAW_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/wuyuncuo/Compiled-Sub/main/v2ray.txt",
    "https://raw.githubusercontent.com/asfytw/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix"
]

def check_server_alive(host, port):
    """Sunucunun IP ve Portuna arkadan gizlice ping atar, kapalıysa eler"""
    try:
        # En fazla 2 saniye bekler, cevap yoksa engelli sayar
        with socket.create_connection((host, int(port)), timeout=2.0):
            return True
    except:
        return False

def main():
    print("[+] Canli link avlama motoru baslatildi...")
    all_raw_text = ""
    
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                all_raw_text += response.read().decode('utf-8', errors='ignore') + "\n"
        except:
            continue

    pattern = r'(vless|vmess|trojan|ss|ssr|hysteria|tuic)://[^\s"\'<>]+'
    extracted_links = re.findall(pattern, all_raw_text, re.IGNORECASE)
    unique_links = list(set(extracted_links))
    
    # Sadece sansürü delme ihtimali en yüksek ana portlar
    allowed_ports = [":443", ":80"]
    
    final_links = []
    print(f"[*] Toplam {len(unique_links)} link analiz ediliyor, canlilar ayiklaniyor...")

    for link in unique_links:
        if any(port in link for port in allowed_ports):
            # Regex ile linkin içindeki IP/Domain ve Port kısmını ayırıyoruz
            # Örnek: vless://uuid@domain.com:443 -> domain.com ve 443'ü çeker
            match = re.search(r'@([^:/]+):([0-9]+)', link)
            if match:
                host = match.group(1)
                port = match.group(2)
                
                # Sadece port kontrolü yetmez, sunucu gerçekten ayakta mı bak
                if check_server_alive(host, port):
                    final_links.append(link)
                    # Çok uzun sürmesin diye ilk canlı 50 taneyi bulunca durdurabilirsin
                    if len(final_links) >= 50:
                        break

    print(f"[+] Filtreleme bitti! Tamamen canli {len(final_links)} adet link bulundu.")

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for link in final_links:
            f.write(link + "\n")
            
    print("[+] 'toplanan_linkler.txt' sadece calisanlarla guncellendi!")

if __name__ == "__main__":
    main()
