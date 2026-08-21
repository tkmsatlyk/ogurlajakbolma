import urllib.request
import urllib.parse
import re
import os

CHANNELS = [
    "https://t.me/s/ares_happ",
    "https://t.me/s/happvpn"
]

COUNTRY_NAMES = [
    "🇩🇪 𝐆𝐞𝐫𝐦𝐚𝐧𝐲", "🇳🇱 𝐍𝐞𝐭𝐡𝐞𝐫𝐥𝐚𝐧𝐝𝐬", "🇺🇸 𝐔𝐧𝐢𝐭𝐞𝐝 𝐒𝐭𝐚𝐭𝐞𝐬", "🇬🇧 𝐔𝐧𝐢𝐭𝐞𝐝 𝐊𝐢𝐧𝐠𝐝𝐨𝐦",
    "🇫🇷 𝐅𝐫𝐚𝐧𝐜𝐞", "🇹🇷 🇹𝐮𝐫𝐤𝐞𝐲", "🇷🇺 🇷𝐮𝐬𝐬𝐢𝐚", "🇷🇴 𝐑𝐨𝐦𝐚𝐧𝐢𝐚",
    "🇨🇭 𝐒𝐰𝐢𝐭𝐳𝐞𝐫𝐥𝐚𝐧𝐝", "🇸🇪 𝐒𝐰𝐞𝐝𝐞𝐧", "🇵🇱 🇵𝐨𝐥𝐚𝐧𝐝", "🇮🇹 🇮𝐭𝐚𝐥𝐲",
    "🇧🇬 𝐁𝐮𝐥𝐠𝐚𝐫𝐢𝐚", "🇦🇹 🇦𝐮𝐬𝐭𝐫𝐢𝐚", "🇨🇦 𝐊𝐚𝐧𝐚𝐝𝐚", "🇸🇬 𝐒𝐢𝐧𝐠𝐚𝐩𝐨𝐫𝐞",
    "🇯🇵 𝐉𝐚𝐩𝐚𝐧", "🇰🇷 𝐒𝐨𝐮𝐭𝐡 𝐊𝐨𝐫𝐞𝐚", "🇦🇪 𝐔𝐧𝐢𝐭𝐞𝐝 𝐀𝐫𝐚𝐛 𝐄𝐦𝐢𝐫𝐚𝐭𝐞𝐬",
    "🇰🇿 𝐊𝐚𝐳𝐚𝐤𝐡𝐬𝐭𝐚𝐧", "🇦🇺 🇦𝐮𝐬𝐭𝐫𝐚𝐥𝐢𝐚", "🇭🇰 𝐇𝐨𝐧𝐠 𝐊𝐨𝐧𝐠", "🇳🇴 🇳𝐨𝐫𝐰𝐚𝐲",
    "🇵🇹 𝐏𝐨𝐫𝐭𝐮𝐠𝐚𝐥", "🇮🇳 🇮𝐧𝐝𝐢𝐚"
]

def fetch_url(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[Net Error] {url}: {e}")
        return ''

def decode_happ(happ_url):
    try:
        decoder_url = "https://happy-decoder.cc/"
        data = urllib.parse.urlencode({'url': happ_url}).encode('utf-8')
        req = urllib.request.Request(
            decoder_url, 
            data=data, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
        match = re.search(r'<textarea[^>]*>(.*?)</textarea>', html, re.DOTALL)
        search_text = match.group(1) if match else html
        found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', search_text)
        return [l.replace('&amp;', '&').replace('&quot;', '').strip() for l in found]
    except Exception as e:
        print(f"[Decoder Error] {e}")
        return []

def main():
    print("--- Kesin Çözüm VPN Toplayıcı Başlatıldı ---")
    
    # KODLARY dosyasını oku, ilk 12 satırı al
    header = []
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "r", encoding="utf-8") as f:
                header = f.read().splitlines()[:12]
        except Exception as e:
            print(f"Header okuma hatası: {e}")
    
    if not header:
        header = [f"# Line {i+1}" for i in range(12)]

    final_nodes = []

    for channel_url in CHANNELS:
        print(f"Taranıyor: {channel_url}")
        html = fetch_url(channel_url)
        if not html:
            continue
        
        # Telegram mesaj bloklarını yakala
        msg_blocks = re.findall(r'<div[^>]*class="[^"]*tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        
        for block in msg_blocks:
            # 1. HTML içindeki href="..." etiketlerinden linkleri sök al (Telegram linkleri buraya saklar!)
            href_links = re.findall(r'href="([^"]+)"', block)
            for link in href_links:
                clean_l = link.replace('&amp;', '&').replace('&quot;', '').strip()
                if clean_l.startswith('happ://'):
                    print(f"Bulunan happ linki (href): {clean_l}")
                    decoded = decode_happ(clean_l)
                    for node in decoded:
                        if node not in final_nodes and not re.search(r'[<>"\s\']', node):
                            final_nodes.append(node)
                elif clean_l.startswith(('vless://', 'vmess://', 'ss://', 'trojan://')):
                    if clean_l not in final_nodes and not re.search(r'[<>"\s\']', clean_l):
                        final_nodes.append(clean_l)

            # 2. Blok içindeki düz metin linklerini de tara
            clean_text = re.sub(r'<[^>]+>', ' ', block)
            text_links = re.findall(r'(?:happ|vless|vmess|ss|trojan)://[^\s<>"\']+', clean_text)
            for link in text_links:
                clean_l = link.replace('&amp;', '&').replace('&quot;', '').strip()
                if clean_l.startswith('happ://'):
                    print(f"Bulunan happ linki (text): {clean_l}")
                    decoded = decode_happ(clean_l)
                    for node in decoded:
                        if node not in final_nodes and not re.search(r'[<>"\s\']', node):
                            final_nodes.append(node)
                elif clean_l.startswith(('vless://', 'vmess://', 'ss://', 'trojan://')):
                    if clean_l not in final_nodes and not re.search(r'[<>"\s\']', clean_l):
                        final_nodes.append(clean_l)

    if not final_nodes:
        print("Uyarı: Yeni node bulunamadı, mevcut KODLARY dosyası korundu.")
        return

    print(f"Toplam {len(final_nodes)} node toplandı.")

    # Ülke formatlaması
    formatted = []
    for i, link in enumerate(final_nodes):
        clean_l = link.split('#')[0]
        country = COUNTRY_NAMES[i % len(COUNTRY_NAMES)]
        formatted.append(f"{clean_l}#{urllib.parse.quote(country)}")

    # Dosyaya yazma
    final_content = header + formatted
    try:
        with open("KODLARY.tmp", "w", encoding="utf-8") as f:
            f.write("\n".join(final_content))
        os.replace("KODLARY.tmp", "KODLARY")
        print("KODLARY dosyası başarıyla güncellendi!")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
