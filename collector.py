import urllib.request
import re
import base64

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 0
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Kripto Çözücü Zırhlı VIP Havuz 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# En sağlam zırhlı ve güncel havuz kaynakları
RAW_SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt",
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat"
]

def decode_if_base64(text):
    """Eğer veri şifreli (Base64) ise gizemi çözer, düz metne çevirir"""
    try:
        # Boşlukları ve satır başlarını temizle
        clean_text = text.strip().replace("\n", "").replace("\r", "")
        # Base64 tamamlayıcı eşitlemelerini ayarla
        clean_text += "=" * ((4 - len(clean_text) % 4) % 4)
        decoded_bytes = base64.b64decode(clean_text)
        return decoded_bytes.decode('utf-8', errors='ignore')
    except:
        # Şifreli değilse normal düz metindir, aynen geri yolla
        return text

def main():
    print("[+] VØRÐR Kripto Çözücü Motor Başlatıldı...")
    all_raw_text = ""
    
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                raw_data = response.read().decode('utf-8', errors='ignore')
                
                # Önce verinin şifresini çözmeyi dene
                decoded_data = decode_if_base64(raw_data)
                
                # Eğer tek bir büyük base64 bloğu çözüldüyse veya düz metindeyse ekle
                all_raw_text += decoded_data + "\n"
        except:
            continue

    # Protokolleri eksiksiz yakalayan en esnek formül
    pattern = r'(vless|vmess|trojan|ss|ssr|hysteria|tuic)://[^\s"\'<>]+'
    extracted_links = re.findall(pattern, all_raw_text, re.IGNORECASE)
    unique_links = list(set(extracted_links))
    
    final_links = []
    
    # Türkmenistan Wi-Fi'ını delme ihtimali olan Cloudflare/Worker ve temiz 443 portlu linkleri cımbızla seç
    for link in unique_links:
        link_lower = link.lower()
        if any(keyword in link_lower for keyword in ["worker", "cloudflare", "pages.dev", "trycloudflare", ":443"]):
            final_links.append(link)

    print(f"[+] Şifreler kırıldı! Filtreye uyan {len(final_links)} adet VIP zırhlı link yazılıyor.")

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for link in final_links:
            f.write(link + "\n")
            
    print("[+] 'toplanan_linkler.txt' başarıyla dolduruldu!")

if __name__ == "__main__":
    main()
