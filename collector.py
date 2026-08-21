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
    print("--- Senin İstediğin Sistemle Çalışan Bot Başlatıldı ---")
    
    channel_url = "https://t.me/s/happvpn"
    
    # 1. Adım: Kanaldan en taze happ:// crypt kodunu çek
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

    happ_links = re.findall(r'happ://[^\s<>"\']+', html)
    href_happ = re.findall(r'href="([^"]+happ://[^"]+)"', html)
    all_happ = list(set(happ_links + href_happ))

    if not all_happ:
        print("Kanalda hiç crypt linki bulunamadı.")
        return

    latest_happ = all_happ[-1].replace('&amp;', '&').replace('&quot;', '').strip()
    print(f"1. Adım Tamam - Bulunan Crypt Link: {latest_happ}")

    # 2. Adım: Decoder'a gönderip çıkan https:// linkini (veya siteyi) al
    target_https_url = ""
    try:
        decoder_url = "https://happy-decoder.cc/"
        print("2. Adım - Crypt link decoder'a gönderilip çözülüyor...")
        
        if HAS_CURL_CFFI:
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

        # Decoder'ın sayfada verdiği https:// linkini bul (<a> etiketleri içinden veya düz metinden)
        hrefs = re.findall(r'href="([^"]+)"', dec_html)
        for h in hrefs:
            if h.startswith('https://') and 'happy-decoder.cc' not in h:
                target_https_url = h
                break
        
        if not target_https_url:
            # Eğer href içinde bulamazsa düz metindeki https linklerine bak
            all_https = re.findall(r'https?://[^\s<>"\']+', dec_html)
            for u in all_https:
                if 'happy-decoder.cc' not in u:
                    target_https_url = u
                    break

        print(f"Decoder'dan çıkan https:// hedef link: {target_https_url}")
        
    except Exception as e:
        print(f"Decoder Hatası: {e}")

    if not target_https_url:
        print("Decoder'dan https linki çıkarılamadı.")
        return

    # 3. Adım: O çıkan https:// linkine gidip (tarayıcı gibi) aç ve içindeki VPN linklerini al
    vpn_nodes = []
    try:
        print(f"3. Adım - Çıkan https linki açılıyor ve VPN linkleri toplanıyor...")
        if HAS_CURL_CFFI:
            resp_page = c_requests.get(target_https_url, impersonate="chrome120", timeout=25)
            page_html = resp_page.text
        else:
            req_page = urllib.request.Request(
                target_https_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
            )
            with urllib.request.urlopen(req_page, timeout=25) as page_resp:
                page_html = page_resp.read().decode('utf-8', errors='ignore')

        found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', page_html)
        vpn_nodes = [l.replace('&amp;', '&').replace('&quot;', '').strip() for l in found_nodes]
        
    except Exception as e:
        print(f"Hedef sayfa açılırken hata: {e}")

    if not vpn_nodes:
        print("Açılan sayfada hiç VPN linki bulunamadı.")
        return

    print(f"Başarıyla alınan VPN link sayısı: {len(vpn_nodes)}")

    # 4. Adım: KODLARY dosyasına KESİNLİKLE DOKUNMA, sadece Toplanan_linkler.txt dosyasına yaz
    try:
        with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(vpn_nodes))
        print("İşlem tamam! Linkler sadece 'Toplanan_linkler.txt' dosyasına yazıldı. KODLARY yerinde duruyor.")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
