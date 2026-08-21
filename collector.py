import urllib.request
import urllib.parse
import json
import re
import html

try:
    from curl_cffi import requests as c_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

def main():
    print("--- Detaylı Debug Destekli Bot Başlatıldı ---")
    
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

    # 2. Adım: Decoder'a istek at ve JSON/HTML olarak çözümle
    decoder_url = "https://happy-decoder.cc/"
    form_data = {
        'url': latest_happ,
        'encrypt': 'crypt5',
        'user-agent': 'Happ/3.24.1',
        'hwid': 'on'
    }

    vpn_nodes = []
    response_text = ""

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
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                },
                impersonate="chrome120", 
                timeout=25
            )
            response_text = resp.text
            
            # JSON yanıt gelme ihtimaline karşı kontrol
            try:
                json_data = resp.json()
                print("JSON Yanıt Yakalandı:", json_data)
                if isinstance(json_data, dict):
                    for k, v in json_data.items():
                        if isinstance(v, str):
                            if 'vless://' in v or 'vmess://' in v or 'ss://' in v:
                                vpn_nodes.append(v)
                            elif v.startswith('http') and 'happy-decoder.cc' not in v:
                                sub_resp = session.get(v, impersonate="chrome120", timeout=15)
                                found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', sub_resp.text)
                                vpn_nodes.extend(found)
            except:
                pass
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
                response_text = dec_resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Decoder İstek Hatası: {e}")
        return

    # Eğer JSON'dan gelmediyse HTML içinden ayıkla
    if not vpn_nodes and response_text:
        decoded_html = html.unescape(response_text)
        
        # Doğrudan node'lar
        found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', decoded_html)
        vpn_nodes.extend(found)
        
        # Sayfadaki tüm linkleri tara
        if not vpn_nodes:
            urls = re.findall(r'https?://[^\s<>"\']+', decoded_html)
            for u in urls:
                clean_u = u.strip().rstrip('"\'>')
                if 'happy-decoder.cc' not in clean_u and 'cloudflare' not in clean_u and 'schema' not in clean_u:
                    print(f"Aday Sub Link Deneniyor: {clean_u}")
                    try:
                        req_sub = urllib.request.Request(clean_u, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_sub, timeout=15) as sub_r:
                            sub_text = sub_r.read().decode('utf-8', errors='ignore')
                            sub_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', sub_text)
                            if sub_nodes:
                                vpn_nodes.extend(sub_nodes)
                                break
                    except Exception as sub_err:
                        print(f"Sub link hata: {sub_err}")

    if not vpn_nodes:
        print("--- DEBUG: Yanıt İçeriği (İlk 1000 Karakter) ---")
        print(response_text[:1000])
        print("---------------------------------------------")
        print("Kritik Hata: İstek başarılı ancak node veya sub link çıkarılamadı.")
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
