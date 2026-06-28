import urllib.request
import re

# Kanalın web görünümü
URL = "https://t.me/s/aresvpn_2"

def main():
    try:
        # Tarayıcı gibi davranıyoruz
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(URL, headers=headers)
        
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8')
            
            # Tüm happ:// linklerini bul
            matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            
            if matches:
                # En sonuncusu en güncel olanıdır
                latest = matches[-1]
                
                # Dosyaya yaz (w modu eskisini komple siler, yenisini yazar)
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(f"#profile-title: 《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》\n")
                    f.write(f"#profile-update-interval: 1\n")
                    f.write(f"#subscription-userinfo: upload=0; download=0; total=53687091200; expire=1924992000\n\n")
                    f.write(latest)
                print(f"Başarıyla güncellendi: {latest[:20]}...")
            else:
                print("Link bulunamadı, kanal yapısı değişmiş olabilir.")
                
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
