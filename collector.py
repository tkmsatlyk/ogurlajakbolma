import urllib.request
import urllib.parse
import re
import html

try:
    from curl_cffi import requests as c_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

def main():
    print("--- Dinamik Form Ayrıştırıcılı Decoder Bot Başlatıldı ---")
    
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

    decoder_url = "https://happy-decoder.cc/"
    response_text = ""
    vpn_nodes = []

    print("Decoder ana sayfası yüklenip form alanları taranıyor...")
    try:
        if HAS_CURL_CFFI:
            session = c_requests.Session()
            # 1. GET isteği ile ana sayfayı ve form yapılandırmasını al
            get_resp = session.get(decoder_url, impersonate="chrome120", timeout=20)
            main_html = get_resp.text
            
            # Form içindeki input alanlarını otomatik bul
            form_data = {}
            inputs = re.findall(r'<input[^>]+>', main_html, re.IGNORECASE)
            for inp in inputs:
                name_match = re.search(r'name=["\']([^"\']+)["\']', inp, re.IGNORECASE)
                val_match = re.search(r'value=["\']([^"\']*)["\']', inp, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1)
                    val = val_match.group(1) if val_match else ''
                    form_data[name] = val

            print(f"Bulunan form alanları: {list(form_data.keys())}")

            # Ana input alanına crypt linkini koy
            target_key = 'url'
            for k in form_data.keys():
                if 'url' in k.lower() or 'code' in k.lower() or 'text' in k.lower() or 'input' in k.lower():
                    target_key = k
                    break
            
            form_data[target_key] = latest_happ
            if 'encrypt' in form_data: form_data['encrypt'] = 'crypt5'
            if 'user-agent' in form_data: form_data['user-agent'] = 'Happ/3.24.1'
            if 'hwid' in form_data: form_data['hwid'] = 'on'

            # 2. POST isteği gönder
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
            response_text = resp.text
        else:
            data = urllib.parse.urlencode({'url': latest_happ}).encode('utf-8')
            req_dec = urllib.request.Request(decoder_url, data=data, headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req_dec, timeout=25) as dec_resp:
                response_text = dec_resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Decoder İstek Hatası: {e}")
        return

    # Yanıtı çözümle
    if response_text:
        decoded_html = html.unescape(response_text)
        
        # A) Doğrudan node'lar
        found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', decoded_html)
        vpn_nodes.extend(found_nodes)

        # B) Textarea taraması
        textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', decoded_html, re.DOTALL | re.IGNORECASE)
        for ta in textareas:
            ta_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', ta)
            vpn_nodes.extend(ta_nodes)

        # C) Sub link taraması
        if not vpn_nodes:
            print("Sub linkler taranıyor...")
            urls = re.findall(r'https?://[^\s<>"\']+', decoded_html)
            for u in urls:
                clean_u = u.strip().rstrip('"\'>')
                if 'happy-decoder.cc' not in clean_u and 'cloudflare' not in clean_u and 'schema' not in clean_u and 'w3.org' not in clean_u:
                    print(f"Aday Sub Link Deneniyor: {clean_u}")
                    try:
                        if HAS_CURL_CFFI:
                            sub_resp = session.get(clean_u, impersonate="chrome120", timeout=15)
                            sub_text = sub_resp.text
                        else:
                            req_sub = urllib.request.Request(clean_u, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req_sub, timeout=15) as sub_r:
                                sub_text = sub_r.read().decode('utf-8', errors='ignore')
                        
                        sub_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', sub_text)
                        if sub_nodes:
                            vpn_nodes.extend(sub_nodes)
                            break
                    except Exception as sub_err:
                        print(f"Sub link çekilirken hata: {sub_err}")

    if not vpn_nodes:
        print("--- DEBUG: Yanıt İçeriği (İlk 1000 Karakter) ---")
        print(response_text[:1000])
        print("---------------------------------------------")
        print("Kritik Hata: Dinamik form gönderildi ancak hâlâ node çıkarılamadı.")
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
