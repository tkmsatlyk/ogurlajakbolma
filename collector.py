import urllib.request
import base64
import re

def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    # 1. Kanalı tara
    req = urllib.request.Request("https://t.me/s/aresvpn_2", headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
        if not matches: return

    # 2. O linkin İÇİNE GİR
    latest_url = matches[-1]
    with urllib.request.urlopen(latest_url) as sub_res:
        content = sub_res.read()
        
        # 3. İÇERİĞİ SÖK (Base64 decode)
        try:
            # Önce base64 ise çöz
            decoded = base64.b64decode(content).decode('utf-8')
        except:
            decoded = content.decode('utf-8')
            
        # 4. SADECE SUNUCULARI AYIKLA
        # vless, vmess, ss, trojan ile başlayan satırları al
        servers = [line for line in decoded.splitlines() if '://' in line]
        
        # 5. DOSYAYA YAZ
        with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(servers))
    
    print(f"Toplam {len(servers)} adet sunucu başarıyla dosyaya işlendi.")

if __name__ == "__main__":
    main()
