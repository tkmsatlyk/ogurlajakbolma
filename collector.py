import urllib.request

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱_》
#profile-update-interval: 1
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ %100 Ham ve Sınırsız VIP Havuz 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# O proların doğrudan uygulamaya yapıştırılan ANA abonelik linkleri
RAW_SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/main/sub/mix",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/v2ray/mix.txt",
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat"
]

def main():
    print("[+] VØRÐR Ham Kopyalama Motoru Başlatıldı...")
    collected_content = ""
    
    for url in RAW_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                # Sitede ne var ne yoksa ham metin olarak çek
                raw_text = response.read().decode('utf-8', errors='ignore')
                collected_content += raw_text + "\n"
        except Exception as e:
            print(f"[-] Kaynak çekilemedi: {url} -> {e}")

    # Gelen ham veriyi satır satır bölüp temizleyelim
    lines = collected_content.splitlines()
    final_lines = []
    
    for line in lines:
        clean_line = line.strip()
        # Boş satırları ve bizim eski başlıkları ekleme, geri kalan her şeyi (şifreli bloklar dahil) al
        if clean_line and not clean_line.startswith("#"):
            final_lines.append(clean_line)

    # Mükerrer (aynı) satırları temizle
    unique_lines = list(set(final_lines))

    print(f"[+] Filtreler sıfırlandı. Toplam {len(unique_lines)} satır veri yazılıyor.")

    # Dosyayı sıfırla, başlığı mühürle ve ham veriyi bas
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for item in unique_lines:
            f.write(item + "\n")
            
    print("[+] 'toplanan_linkler.txt' ham verilerle dolduruldu!")

if __name__ == "__main__":
    main()
