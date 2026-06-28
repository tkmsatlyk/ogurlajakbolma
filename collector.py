import urllib.request
import base64
import re

def main():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request("https://t.me/s/aresvpn_2", headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            
            if not matches:
                print("Kanalda kod bulunamadı.")
                return
            
            latest_url = matches[-1]
            print(f"URL: {latest_url}")
            
            # Linke git
            req_sub = urllib.request.Request(latest_url, headers=headers)
            with urllib.request.urlopen(req_sub, timeout=30) as sub_res:
                content = sub_res.read()
                
                # BİLGİYİ GÖRMEK İÇİN YAZDIRIYORUZ
                print("Ham Veri Uzunluğu:", len(content))
                
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                    print("Decode edilmiş veri:", decoded[:100]) # İlk 100 karakteri göster
                except:
                    decoded = content.decode('utf-8')
                    print("Decode edilemedi, ham veri:", decoded[:100])
                
                servers = [line for line in decoded.splitlines() if '://' in line]
                print(f"Bulunan sunucu sayısı: {len(servers)}")
                
                if len(servers) > 0:
                    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                        f.write("\n".join(servers))
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
