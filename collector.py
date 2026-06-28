import urllib.request
import base64
import re

# Telegram kanalının web arayüzü
CHANNEL_URL = "https://t.me/s/aresvpn_2"

def main():
    try:
        # Telegram kanalını gerçek bir tarayıcı gibi ziyaret et
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(CHANNEL_URL, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # 1. EN SON PAYLAŞILAN MESAJI BUL (Kanalın en tepesindeki linki al)
            # Telegram 't.me/s/' linklerinde mesajlar en tepeden başlar, bu yüzden ilk eşleşme en yenisidir.
            match = re.search(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            
            if not match:
                print("[-] Kanalda yeni kod bulunamadı.")
                return
            
            latest_url = match.group(0)
            print(f"[+] En taze kod yakalandı: {latest_url}")
            
            # 2. O YENİ LİNKİN İÇİNE GİR VE SUNUCULARI SÖK
            req_sub = urllib.request.Request(latest_url, headers=headers)
            with urllib.request.urlopen(req_sub, timeout=30) as sub_res:
                content = sub_res.read()
                
                # Base64 çözümü (Abonelik içeriğini açar)
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                except:
                    decoded = content.decode('utf-8')
                
                # Sadece '://' içeren gerçek sunucu satırlarını filtrele (Çöpü siliyor)
                servers = [line for line in decoded.splitlines() if '://' in line]
                
                # 3. ESKİYİ SİL VE YENİYİ YAZ
                # 'w' modu, dosyanın içindeki tüm eski sunucuları siler ve listeyi günceller.
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(servers))
                
                print(f"[+] {len(servers)} adet taze sunucu başarıyla dosyaya işlendi.")

    except Exception as e:
        print(f"[-] Hata oluştu: {e}")

if __name__ == "__main__":
    main()
