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
    print("--- Oturumlu ve Güvenlik Korumalı Decoder Bot Başlatıldı ---")
    
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

    # 2. Adım: Oturum açarak (Cookie/Session) decoder sitesine istek at
    decoder_url = "https://happy-decoder.cc/"
    dec_html = ""
    
    form_data = {
        'url': latest_happ,
        'encrypt': 'crypt5',
        'user-agent': 'Happ/3.24.1',
        'hwid': 'on'
    }

    print("Decoder sitesine oturum başlatılarak istek gönderiliyor...")
    try:
        if HAS_CURL_CFFI:
            # Oturum nesnesi oluşturup önce ana sayfayı ziyaret ediyoruz (Çerez ve oturum almak için)
            session = c_requests.Session()
            session.get(decoder_url, impersonate="chrome120", timeout=20)
            
            resp = session.post(
                decoder_url, 
                data=form_data, 
                headers={
                    'Referer': decoder_url,
                    'Origin': 'https://happy-decoder.cc',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                impersonate="chrome120", 
                timeout=25
            )
            dec_html = resp.text
            print(f"Decoder Yanıt Kodu: {resp.status_code}, Uzunluk: {len(dec_html)}")
        else:
            data = urllib.parse.urlencode(form_data).encode('utf-8')
            req_dec = urllib.request.Request(
                decoder_url, 
                data=data, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': decoder_url
                }
            )
            with urllib.request.urlopen(req_dec, timeout=25) as dec_resp:
                dec_html = dec_resp.read().decode('utf-8', errors='ignore')
            print(f"Decoder Yanıt Uzunluğu: {len(dec_html)}")
    except Exception as e:
        print(f"Decoder İstek Hatası: {e}")
        return

    vpn_nodes = []
    try:
        # A) Sayfada doğrudan vless:// vmess:// varsa topla
        found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', dec_html)
        vpn_nodes = [l.replace('&amp;', '&').replace('&quot;', '').strip() for l in found_nodes]

        # B) Sub linkini ara ve içeriğine git
        if not vpn_nodes:
            print("Doğrudan node çıkmadı, HTML içindeki sub linkleri taranıyor...")
            all_urls = re.findall(r'https?://[^\s<>"\']+', dec_html)
            for sub_url in all_urls:
                clean_sub = urllib.parse.unquote(sub_url.replace('&amp;', '&').replace('&quot;', '').strip().rstrip('"\'>'))
                if 'happy-decoder.cc' not in clean_sub and 'cloudflare' not in clean_sub:
                    print(f"Aday Sub Link Bulundu: {clean_sub}")
                    try:
                        if HAS_CURL_CFFI:
                            sub_resp = c_requests.get(clean_sub, impersonate="chrome120", timeout=25)
                            sub_text = sub_resp.text
                        else:
                            req_sub = urllib.request.Request(clean_sub, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req_sub, timeout=25) as sub_r:
                                sub_text = sub_r.read().decode('utf-8', errors='ignore')
                        
                        sub_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', sub_text)
                        if sub_nodes:
                            vpn_nodes.extend([l.replace('&amp;', '&').replace('&quot;', '').strip() for l in sub_nodes])
                            print(f"Sub linkten {len(sub_nodes)} adet VPN node'u çekildi!")
                            break
                    except Exception as sub_err:
                        print(f"Sub link açılırken hata: {sub_err}")

    except Exception as e:
        print(f"İçerik Çözümleme Hatası: {e}")

    if not vpn_nodes:
        print("Kritik Hata: İstek atıldı ancak VPN linki elde edilemedi.")
        print(f"Gelen HTML'in ilk 300 karakteri: {dec_html[:300]}")
        return

    # Tekrarlanan linkleri temizle
    vpn_nodes = list(dict.fromkeys(vpn_nodes))
    print(f"Toplam {len(vpn_nodes)} adet VPN linki başarıyla toplandı.")

    # 3. Adım: KODLARY dosyasına KESİNLİKLE DOKUNMA, sadece Toplanan_linkler.txt dosyasına yaz
    try:
        with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(vpn_nodes))
        print("İşlem başarıyla tamamlandı! Linkler sadece 'Toplanan_linkler.txt' dosyasına yazıldı. KODLARY yerinde duruyor.")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
