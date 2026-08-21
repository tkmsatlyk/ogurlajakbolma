import urllib.request
import urllib.parse
import re
import html

try:
    from curl_cffi import requests as c_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

def fetch_sub_nodes(sub_url):
    try:
        if HAS_CURL_CFFI:
            sub_resp = c_requests.get(sub_url, impersonate="chrome120", timeout=25)
            sub_text = sub_resp.text
        else:
            req_sub = urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_sub, timeout=25) as sub_r:
                sub_text = sub_r.read().decode('utf-8', errors='ignore')
        
        nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', sub_text)
        return [l.replace('&amp;', '&').replace('&quot;', '').strip() for l in nodes]
    except Exception as e:
        print(f"Sub link çekilemedi ({sub_url}): {e}")
        return []

def main():
    print("--- HTML Ayrıştırıcılı Profesyonel Bot Başlatıldı ---")
    
    channel_url = "https://t.me/s/happvpn"
    
    # 1. Adım: Kanaldan en taze happ:// crypt kodunu çek
    try:
        req = urllib.request.Request(
            channel_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html_content = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Kanal çekilemedi: {e}")
        return

    happ_links = re.findall(r'happ://[^\s<>"\']+', html_content)
    href_happ = re.findall(r'href="([^"]+happ://[^"]+)"', html_content)
    all_happ = list(set(happ_links + href_happ))

    if not all_happ:
        print("Kanalda hiç crypt linki bulunamadı.")
        return

    latest_happ = all_happ[-1].replace('&amp;', '&').replace('&quot;', '').strip()
    print(f"Bulunan Crypt Link: {latest_happ}")

    # 2. Adım: Decoder'a oturumlu istek at
    decoder_url = "https://happy-decoder.cc/"
    dec_html = ""
    
    form_data = {
        'url': latest_happ,
        'encrypt': 'crypt5',
        'user-agent': 'Happ/3.24.1',
        'hwid': 'on'
    }

    print("Decoder sitesine istek gönderiliyor...")
    try:
        if HAS_CURL_CFFI:
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
    except Exception as e:
        print(f"Decoder İstek Hatası: {e}")
        return

    vpn_nodes = []
    try:
        decoded_html = html.unescape(dec_html)

        # A) Sayfa genelinde direkt vless/vmess var mı bak
        found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', decoded_html)
        vpn_nodes.extend(found_nodes)

        # B) <textarea> etiketlerinin içini tara (Sonuçların basıldığı ana yer)
        textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', decoded_html, re.DOTALL | re.IGNORECASE)
        for ta in textareas:
            ta_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', ta)
            vpn_nodes.extend(ta_nodes)
            
            ta_urls = re.findall(r'https?://[^\s<>"\']+', ta)
            for u in ta_urls:
                if 'happy-decoder.cc' not in u:
                    clean_u = u.strip().rstrip('"\'>')
                    print(f"Textarea içinde sub link bulundu: {clean_u}")
                    vpn_nodes.extend(fetch_sub_nodes(clean_u))

        # C) Input value özniteliklerini tara (Abonelik linklerinin gizlendiği yer)
        input_values = re.findall(r'value=["\'](https?://[^"\']+)["\']', decoded_html, re.IGNORECASE)
        for val in input_values:
            if 'happy-decoder.cc' not in val and 'cloudflare' not in val:
                print(f"Input value içinde sub link bulundu: {val}")
                vpn_nodes.extend(fetch_sub_nodes(val))

        # D) Genel arama
        if not vpn_nodes:
            print("Genel URL havuzu taranıyor...")
            all_urls = re.findall(r'https?://[^\s<>"\']+', decoded_html)
            for sub_url in all_urls:
                clean_sub = urllib.parse.unquote(sub_url.replace('&amp;', '&').replace('&quot;', '').strip().rstrip('"\'>'))
                if 'happy-decoder.cc' not in clean_sub and 'cloudflare' not in clean_sub and 'schema' not in clean_sub:
                    print(f"Aday Sub Link Deneniyor: {clean_sub}")
                    sub_nodes = fetch_sub_nodes(clean_sub)
                    if sub_nodes:
                        vpn_nodes.extend(sub_nodes)
                        break

    except Exception as e:
        print(f"İçerik Çözümleme Hatası: {e}")

    if not vpn_nodes:
        print("Kritik Hata: HTML alındı ancak node veya sub link çıkarılamadı.")
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
