import urllib.request
import base64
import re
import os

def main():
    try:
        # 1. Telegram kanalından en güncel linki al
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request("https://t.me/s/aresvpn_2", headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            
            if not matches:
                print("Kanalda kod bulunamadı!")
                return
            
            latest_url = matches[-1]
            
            # 2. Linkin içeriğini çek
            req_sub = urllib.request.Request(latest_url, headers=headers)
            with urllib.request.urlopen(req_sub, timeout=30) as sub_res:
                content = sub_res.read()
                try:
                    # Base64 çözümü
                    decoded = base64.b64decode(content).decode('utf-8')
                except:
                    decoded = content.decode('utf-8')
                
                # Sadece sunucu linklerini ayıkla
                servers = [line for line in decoded.splitlines() if '://' in line]
                
                # 3. DOSYAYI ZORLA YAZ VE KAPAT
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(servers))
                
                print(f"Toplam {len(servers)} adet link 'toplanan_linkler.txt' dosyasına yazıldı.")
                
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    main()
