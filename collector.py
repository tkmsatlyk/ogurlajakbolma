import urllib.request
import base64
import re

def main():
    # 1. Telegram kanalından en son linki al
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request("https://t.me/s/aresvpn_2", headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            # En son paylaşılan linki yakala
            matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            if not matches:
                print("Link bulunamadı.")
                return
            latest_url = matches[-1]
            
            # 2. O linkin içine gir (Panel içeriğini sök)
            req_sub = urllib.request.Request(latest_url, headers=headers)
            with urllib.request.urlopen(req_sub, timeout=30) as sub_res:
                content = sub_res.read()
                # Base64 çözümlemesi
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                except:
                    decoded = content.decode('utf-8')
                
                # 3. İÇERİĞİ TEMİZLE (Sunucu listesini ayıkla)
                # '://' içeren tüm satırları al, çöp verileri at
                servers = [line for line in decoded.splitlines() if '://' in line]
                
                # 4. DOSYAYA YAZ
                if servers:
                    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                        f.write("\n".join(servers))
                    print(f"Başarıyla {len(servers)} sunucu güncellendi.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
