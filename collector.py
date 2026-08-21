import urllib.request
import urllib.parse
import re
import os
import sys

def fetch_raw(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""

def decode_happ(happ_link):
    try:
        # Decode isteği
        data = urllib.parse.urlencode({'url': happ_link}).encode('utf-8')
        req = urllib.request.Request("https://happy-decoder.cc/", data=data, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            # Çözülmüş linkleri al
            found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', content)
            return [l.strip() for l in found]
    except:
        return []

def main():
    # 1. KODLARY Oku
    if not os.path.exists("KODLARY"):
        print("Dosya yok!")
        sys.exit(1)
        
    with open("KODLARY", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        header = lines[:12]

    # 2. Telegram'dan Çek
    html = fetch_raw("https://t.me/s/happvpn")
    
    # 3. İçinden linkleri ayıkla (regex'i geniş tuttum)
    happ_links = re.findall(r'(happ://[^\s<>"\']+|vless://[^\s<>"\']+|vmess://[^\s<>"\']+|ss://[^\s<>"\']+|trojan://[^\s<>"\']+)', html)
    
    final_nodes = []
    
    for link in set(happ_links): # set() ile tekrar edenleri temizle
        if link.startswith("happ://"):
            # Çözücüye yolla
            decoded = decode_happ(link)
            final_nodes.extend(decoded)
        else:
            # Doğrudan link ise ekle
            final_nodes.append(link)

    if not final_nodes:
        print("Hiç node bulunamadı.")
        sys.exit(1)

    # 4. Yaz
    countries = ["🇩🇪 Germany", "🇳🇱 Netherlands", "🇺🇸 USA", "🇬🇧 UK", "🇫🇷 France", "🇹🇷 Turkey", "🇷🇺 Russia", "🇷🇴 Romania"]
    formatted = []
    for i, node in enumerate(final_nodes[:50]): # İlk 50 yeterli
        clean_node = node.split('#')[0]
        country = countries[i % len(countries)]
        formatted.append(f"{clean_node}#{urllib.parse.quote(country)}")

    with open("KODLARY.tmp", "w", encoding="utf-8") as f:
        f.write("\n".join(header + formatted))
    
    os.replace("KODLARY.tmp", "KODLARY")
    print(f"İşlem tamamlandı! {len(formatted)} node eklendi.")

if __name__ == "__main__":
    main()
