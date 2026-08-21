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
    print("--- Ekran Görüntüsü Mantığıyla Çalışan Çözücü Başlatıldı ---")
    
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
    print(f"Bulunan Crypt Link: {latest_happ}")

    # 2. Adım: Decoder'a gönderip çözülmüş sayfayı al
    vpn_nodes = []
    decoder_url = "https://happy-decoder.cc/"
    
    try:
        print("Crypt link decoder'a gönderiliyor...")
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

        # A) Decoder sayfasının içinde direkt vless:// vmess:// yazıyorsa onları al
        found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', dec_html)
        vpn_nodes = [l.replace('&amp;', '&').replace('&quot;', '').strip() for l in found_nodes]

        # B) Eğer doğrudan çıkmadıysa, ekran görüntüsündeki gibi 'РАСШИФРОВАННЫЙ URL' (sub linki) yakalayıp ona istek at
        if not vpn_nodes:
            print("Doğrudan node bulunamadı, alt abonelik (sub) linki aranıyor...")
            sub_links = re.findall(r'https?://[^\s<>"\']+', dec_html)
            for sub_url in sub_links:
                if 'happy-decoder.cc' not in sub_url:
                    clean_sub = sub_url.replace('&amp;', '&').replace('&quot;', '').strip()
                    print(f"Sub link bulundu, içeriği çekiliyor: {clean_sub}")
                    
                    if HAS_CURL_CFFI:
                        sub_resp = c_requests.get(clean_sub, impersonate="chrome120", timeout=25)
                        sub_text = sub_resp.text
                    else:
                        req_sub = urllib.request.Request(clean_sub, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_sub, timeout=25) as sub_r:
                            sub_text = sub_r.read().decode('utf-8', errors='ignore')
                    
                    sub_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', sub_text)
                    vpn_nodes.extend([l.replace('&amp;', '&').replace('&quot;', '').strip() for l in sub_nodes])
                    break

    except Exception as e:
        print(f"Decoder / Çözüm Hatası: {e}")

    if not vpn_nodes:
        print("Hiç VPN linki elde edilemedi.")
        return

    # Aynı linkleri tekrar yazmamak için temizle
    vpn_nodes = list(dict.fromkeys(vpn_nodes))
    print(f"Toplam {len(vpn_nodes)} adet VPN linki başarıyla yakalandı.")

    # 3. Adım: KODLARY dosyasına KESİNLİKLE DOKUNMA, sadece Toplanan_linkler.txt dosyasına yaz
    try:
        with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(vpn_nodes))
        print("İşlem tamam! Linkler sadece 'Toplanan_linkler.txt' dosyasına yazıldı. KODLARY yerinde duruyor.")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
