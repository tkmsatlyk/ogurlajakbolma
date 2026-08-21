import urllib.request
import urllib.parse
import re
import os
import sys

def fetch_html(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

def decode_crypt(crypt_data):
    """Her türlü crypt/şifreli veriyi decoder'a gönderip çözen ana fonksiyon"""
    try:
        # Burada senin kullandığın decoder URL'ini kullanıyoruz
        data = urllib.parse.urlencode({'url': crypt_data}).encode('utf-8')
        req = urllib.request.Request("https://happy-decoder.cc/", data=data, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as dec_resp:
            dec_html = dec_resp.read().decode('utf-8', errors='ignore')
            dec_match = re.search(r'<textarea[^>]*>(.*?)</textarea>', dec_html, re.DOTALL)
            search_target = dec_match.group(1) if dec_match else dec_html
            # Çözülmüş linkleri al
            return re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', search_target)
    except:
        return []

def main():
    print("--- Hub Crypt Çözücü Başlatıldı ---")
    
    header = []
    if os.path.exists("KODLARY"):
        with open("KODLARY", "r", encoding="utf-8") as f:
            header = f.read().splitlines()[:12]
    else:
        print("KODLARY dosyası yok!")
        sys.exit(1)

    final_nodes = []
    channels = ["https://t.me/s/ares_happ", "https://t.me/s/happvpn"]

    for channel in channels:
        html = fetch_html(channel)
        if not html: continue
        
        # Mesaj metinlerini bul
        msg_blocks = re.findall(r'<div[^>]*class="[^"]*tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        
        for block in msg_blocks:
            # 1. Önce doğrudan happ:// linki var mı bak
            happ_links = re.findall(r'happ://[^\s<>"\']+', block)
            # 2. Veya "crypt" içerik mi? (Mesajın tamamını tek bir crypt bloğu gibi dene)
            # Burası önemli: Mesajın içindeki metni doğrudan decoder'a yolluyoruz
            raw_text = re.sub(r'<[^>]+>', ' ', block).strip()
            
            # İçinde link/crypt olan blokları gönder
            if len(raw_text) > 20: # Kısa mesajları geç
                decoded = decode_crypt(raw_text)
                for link in decoded:
                    clean_l = link.replace('&amp;', '&').replace('&quot;', '').strip()
                    if clean_l not in final_nodes and not re.search(r'[<>"\s\']', clean_l):
                        final_nodes.append(clean_l)
                        if len(final_nodes) >= 30: break
            if len(final_nodes) >= 30: break

    # Formatlama
    countries = ["🇩🇪 𝐆𝐞𝐫𝐦𝐚𝐧𝐲", "🇳🇱 𝐍𝐞𝐭𝐡𝐞𝐫𝐥𝐚𝐧𝐝𝐬", "🇺🇸 𝐔𝐧𝐢𝐭𝐞𝐝 𝐒𝐭𝐚𝐭𝐞𝐬", "🇬🇧 𝐔𝐧𝐢𝐭𝐞𝐝 𝐊𝐢𝐧𝐠𝐝𝐨𝐦", "🇫🇷 𝐅𝐫𝐚𝐧𝐜𝐞"]
    formatted = []
    for i, link in enumerate(final_nodes):
        formatted.append(f"{link.split('#')[0]}#{urllib.parse.quote(countries[i % len(countries)])}")

    # Dosyayı 12 satır sabit + yeni linkler şeklinde yaz
    try:
        with open("KODLARY.tmp", "w", encoding="utf-8") as f:
            f.write("\n".join(header + formatted))
        os.replace("KODLARY.tmp", "KODLARY")
        print(f"İşlem tamamlandı! {len(formatted)} node eklendi.")
    except Exception as e:
        print(f"Dosya hatası: {e}")

if __name__ == "__main__":
    main()
