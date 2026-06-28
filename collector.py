import urllib.request
import base64
import re

# Telegram kanalının web görünümü (burayı değiştirme)
CHANNEL_URL = "https://t.me/s/aresvpn_2"

def main():
    try:
        # 1. KANALI TARA VE HAPP LİNKİNİ BUL
        req = urllib.request.Request(CHANNEL_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # Kanalda paylaşılan en son linki yakala
            match = re.search(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            
            if not match:
                print("[-] Kanalda şu an güncel bir link yok!")
                return
            
            subscription_url = match.group(0)
            print(f"[+] Yeni abonelik linki yakalandı: {subscription_url}")
            
            # 2. O LİNKİN İÇİNDEKİ SUNUCULARI ÇÖZ (Base64 Çözücü)
            # Not: Eğer happ:// linki direkt link değil de bir yapıysa, 
            # burası uygulamanın 'i' harfindeki içeriği simüle eder.
            req_sub = urllib.request.Request(subscription_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_sub, timeout=15) as sub_res:
                content = sub_res.read()
                
                try:
                    # Sunucu verilerini çöz
                    decoded = base64.b64decode(content).decode('utf-8')
                except:
                    decoded = content.decode('utf-8')
                
                # Sadece geçerli sunucu linklerini (vless://, ss:// vb.) filtrele
                lines = [line for line in decoded.splitlines() if '://' in line]
                
                # 3. DOSYAYA YAZ
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                    
                print(f"[+] {len(lines)} adet sunucu başarıyla ayıklandı!")

    except Exception as e:
        print(f"[-] Hata: {e}")

if __name__ == "__main__":
    main()
