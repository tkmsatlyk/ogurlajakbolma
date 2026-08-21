import urllib.request
import urllib.parse
import re
import os

try:
    from curl_cffi import requests as c_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

def main():
    print("--- Hub Crypt Deşifre ve Aktarım Aracı Başlatıldı ---")
    
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

    # Sayfadaki tüm happ:// (crypt) linklerini ve href içindekileri yakala
    happ_links = re.findall(r'happ://[^\s<>"\']+', html)
    href_happ = re.findall(r'href="([^"]+happ://[^"]+)"', html)
    all_happ = list(set(happ_links + href_happ))

    if not all_happ:
        print("Kanalda hiç crypt linki bulunamadı.")
        return

    # En taze (en son paylaşılan) crypt link
    latest_happ = all_happ[-1].replace('&amp;', '&').replace('&quot;', '').strip()
    print(f"Bulunan EN TAZE Crypt Link: {latest_happ}")

    # Decoder'a gönderip crypt linkini deşifre et (kır)
    decoded_nodes = []
    try:
        decoder_url = "https://happy-decoder.cc/"
        print("Crypt link decoder'a gönderilip deşifre ediliyor...")
        
        if HAS_CURL_CFFI:
            # Tarayıcı taklidi yaparak engellenmeden kırıyoruz
            resp = c_requests.post(decoder_url, data={'url': latest_happ}, impersonate="chrome120", timeout=25)
            dec_html = resp.text
        else:
            data = urllib.parse.urlencode({'url': latest_happ}).encode('utf-8')
            req_dec = urllib.request.Request(
                decoder_url, 
                data=data, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            with urllib.request.urlopen(req_dec, timeout=25) as dec_resp:
                dec_html = dec_resp.read().decode('utf-8', errors='ignore')

        # Çözülen metnin içinden gerçek VPN linklerini al
        match = re.search(r'<textarea[^>]*>(.*?)</textarea>', dec_html, re.DOTALL)
        search_target = match.group(1) if match else dec_html
        found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', search_target)
        decoded_nodes = [l.replace('&amp;', '&').replace('&quot;', '').strip() for l in found]
        
    except Exception as e:
        print(f"Decoder (Deşifre) Hatası: {e}")

    if not decoded_nodes:
        print("Crypt link deşifre edilemedi veya boş döndü.")
        return

    print(f"Başarıyla deşifre edilen node sayısı: {len(decoded_nodes)}")

    # 1. KODLARY dosyasını tamamen sıfırla / temizle
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "w", encoding="utf-8") as f:
                f.write("")
            print("KODLARY dosyası tamamen sıfırlandı.")
        except Exception as e:
            print(f"KODLARY temizlenirken hata: {e}")

    # 2. Deşifre edilen VPN linklerini 'toplanan linkler' dosyasına aktar
    try:
        with open("toplanan linkler", "w", encoding="utf-8") as f:
            f.write("\n".join(decoded_nodes))
        print("Deşifre edilen linkler başarıyla 'toplanan linkler' dosyasına aktarıldı.")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
