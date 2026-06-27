import urllib.request

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 0
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Pro Geliştiriciler Özel VIP Havuzu 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# Sadece işi gücü kaliteli abonelik hazırlamak olan özel şahısların ana linkleri
RAW_SOURCES = [
    # 1. Senin favori ShadowException abimiz
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    
    # 2. Bafry - Kaliteli Cloudflare ve Reality Ustası
    "https://raw.githubusercontent.com/bafry/v2ray-subscription/main/sub/mix",
    
    # 3. LalatinaHub - Çin sansürünü delen en sağlam toplayıcılardan biri
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/sub/mix",
    
    # 4. Saeid0 - Reality ve gRPC Protokol Canavarı
    "https://raw.githubusercontent.com/Saeid0/v2ray-collector/master/Sub/All_Configs_Sub.txt",
    
    # 5. Snakem7 - Sürekli taze ve elenmiş config basan hesap
    "https://raw.githubusercontent.com/snakem7/v2ray-sub/main/mix",
    
    # 6. NiREvil - İran ağ ortamı için özel ayıklanmış havuz
    "https://raw.githubusercontent.com/NiREvil/v2ray/main/sub/mix",
    
    # 7. vfarid ve yebekhe (Bunlar zaten bu işin kurucuları, listemizde kesin kalmalılar)
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt"
]

def main():
    print("[+] VØRÐR Özel Şahıslar Motoru Başlatıldı...")
    collected_content = ""
    
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=12) as response:
                raw_text = response.read().decode('utf-8', errors='ignore')
                collected_content += raw_text + "\n"
                print(f"[+] Pro şahsın havuzu başarıyla çekildi: {url.split('/')[3]}")
        except:
            continue

    # Ham veriyi satır satır bölüp listeliyoruz
    lines = collected_content.splitlines()
    final_lines = []
    
    for line in lines:
        clean_line = line.strip()
        # Boş satırları ve çöp başlıkları listeye eklemiyoruz
        if clean_line and not clean_line.startswith("#") and not clean_line.startswith("//"):
            final_lines.append(clean_line)

    # Aynı olan linkleri (mükerrerleri) temizle
    unique_lines = list(set(final_lines))

    print(f"[+] {len(unique_lines)} adet elenmiş pro satır başarıyla yazılıyor.")

    # Dosyayı sıfırla ve üzerine mühürle
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for item in unique_lines:
            f.write(item + "\n")
            
    print("[+] 'toplanan_linkler.txt' yeni proların linkleriyle dolduruldu!")

if __name__ == "__main__":
    main()
