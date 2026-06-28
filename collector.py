import urllib.request
import base64
import re
import os

def main():
    # Eski dosyayı her zaman sil, tertemiz başla
    if os.path.exists("toplanan_linkler.txt"):
        os.remove("toplanan_linkler.txt")

    try:
        # Kanalı çek
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request("https://t.me/s/aresvpn_2", headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            
            if not matches:
                return # Kod yoksa dur
            
            # Son (en güncel) linki al
            latest_url = matches[-1]
            
            # İçeriği çek
            req_sub = urllib.request.Request(latest_url, headers=headers)
            with urllib.request.urlopen(req_sub, timeout=30) as sub_res:
                content = sub_res.read()
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                except:
                    decoded = content.decode('utf-8')
                
                # Sadece linkleri al
                servers = [line for line in decoded.splitlines() if '://' in line]
                
                # Yaz
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(servers))
                print("Başarıyla yazıldı.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
