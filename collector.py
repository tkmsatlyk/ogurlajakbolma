import urllib.request
import urllib.parse
import re
import os

def main():
    print("--- En Taze Happ Linki Toplayıcı Başlatıldı ---")
    
    channel_url = "https://t.me/s/happvpn"
    
    try:
        req = urllib.request.Request(
            channel_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Kanal çekilemedi: {e}")
        return

    # Sayfadaki tüm happ:// linklerini ve href içindekileri yakala
    happ_links = re.findall(r'happ://[^\s<>"\']+', html)
    href_happ = re.findall(r'href="([^"]+happ://[^"]+)"', html)
    all_happ = list(set(happ_links + href_happ))

    if not all_happ:
        print("Kanalda hiç happ:// linki bulunamadı.")
        return

    # En taze (en son paylaşılan) link listenin sonundakidir
    latest_happ = all_happ[-1].replace('&amp;', '&').replace('&quot;', '').strip()
    print(f"Bulunan EN TAZE happ linki: {latest_happ}")

    # Decoder'a gönderip çözdür
    decoded_nodes = []
    try:
        data = urllib.parse.urlencode({'url': latest_happ}).encode('utf-8')
        dec_req = urllib.request.Request(
            "https://happy-decoder.cc/", 
            data=data, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        with urllib.request.urlopen(dec_req, timeout=20) as dec_resp:
            dec_html = dec_resp.read().decode('utf-8', errors='ignore')
            match = re.search(r'<textarea[^>]*>(.*?)</textarea>', dec_html, re.DOTALL)
            search_target = match.group(1) if match else dec_html
            found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', search_target)
            decoded_nodes = [l.replace('&amp;', '&').replace('&quot;', '').strip() for l in found]
    except Exception as e:
        print(f"Decoder hatası: {e}")

    if not decoded_nodes:
        print("Decoder bu linki çözemedi veya boş döndü.")
        return

    print(f"Çözülen node sayısı: {len(decoded_nodes)}")

    # 1. KODLARY dosyasını tamamen temizle (içine yazdığımız her şeyi sil)
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "w", encoding="utf-8") as f:
                f.write("")
            print("KODLARY dosyası tamamen temizlendi.")
        except Exception as e:
            print(f"KODLARY temizlenirken hata: {e}")

    # 2. Toplanan linkleri 'toplanan linkler' dosyasına yaz (eski kalıntıları tamamen silip üstüne yaz)
    try:
        with open("toplanan linkler", "w", encoding="utf-8") as f:
            f.write("\n".join(decoded_nodes))
        print("Linkler başarıyla 'toplanan linkler' dosyasına yazıldı.")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
