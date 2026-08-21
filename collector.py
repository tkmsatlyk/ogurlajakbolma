import urllib.request
import urllib.parse
import re
import os
import socket
import time
import random
import http.client

# KOTALAR: 15 + 10 = 25 Link
CHANNELS = {
    "happvpn": {"url": "https://t.me/s/happvpn", "limit": 15, "max_ms": 1500},
    "LonUp_M": {"url": "https://t.me/s/LonUp_M", "limit": 10, "max_ms": 700}
}

COUNTRY_NAMES = [
    "🇩🇪 𝐆𝐞𝐫𝐦𝐚𝐧𝐲", "🇳🇱 𝐍𝐞𝐭𝐡𝐞𝐫𝐥𝐚𝐧𝐝𝐬", "🇺🇸 𝐔𝐧𝐢𝐭𝐞𝐝 𝐒𝐭𝐚𝐭𝐞𝐬", "🇬🇧 𝐔𝐧𝐢𝐭𝐞𝐝 𝐊𝐢𝐧𝐠𝐝𝐨𝐦",
    "🇫🇷 🇫𝐫𝐚𝐧𝐜𝐞", "🇹🇷 🇹𝐮𝐫𝐤𝐞𝐲", "🇷🇺 🇷𝐮𝐬𝐬𝐢𝐚", "🇷🇴 𝐑𝐨𝐦𝐚𝐧𝐢𝐚",
    "🇨🇭 𝐒𝐰𝐢𝐭𝐳𝐞𝐫𝐥𝐚𝐧𝐝", "🇸🇪 𝐒𝐰𝐞𝐝𝐞𝐧", "🇵🇱 𝐏𝐨𝐥𝐚𝐧𝐝", "🇮🇹 𝐈𝐭𝐚𝐥𝐲",
    "🇧🇬 𝐁𝐮𝐥𝐠𝐚𝐫𝐢𝐚", "🇦🇹 🇦𝐮𝐬𝐭𝐫𝐢𝐚", "🇨🇦 𝐊𝐚𝐧𝐚𝐝𝐚", "🇸🇬 𝐒𝐢𝐧𝐠𝐚𝐩𝐨𝐫𝐞",
    "🇯🇵 𝐉𝐚𝐩𝐚𝐧", "🇰🇷 𝐒𝐨𝐮𝐭𝐡 𝐊𝐨𝐫𝐞𝐚", "🇦🇪 𝐔𝐧𝐢𝐭𝐞𝐝 𝐀𝐫𝐚𝐛 𝐄𝐦𝐢𝐫𝐚𝐭𝐞𝐬",
    "🇰🇿 𝐊𝐚𝐳𝐚𝐤𝐡𝐬𝐭𝐚𝐧", "🇦🇺 🇦𝐮𝐬𝐭𝐫𝐚𝐥𝐢𝐚", "🇭🇰 𝐇𝐨𝐧𝐠 𝐊𝐨𝐧𝐠", "🇳🇴 🇳𝐨𝐫𝐰𝐚𝐲",
    "🇵🇹 𝐏𝐨𝐫𝐭𝐮𝐠𝐚𝐥", "🇮🇳 𝐈𝐧𝐝𝐢𝐚"
]

def fetch_url(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Encoding': 'identity'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except http.client.IncompleteRead as e:
        return e.partial.decode('utf-8', errors='ignore')
    except:
        return ''

def clean_and_fix_link(link):
    return link.replace('&amp;', '&').replace('&quot;', '').replace('&#39;', '').strip()

def is_clean_link(link):
    if not any(link.startswith(p) for p in ['vless://', 'vmess://', 'ss://', 'trojan://']):
        return False
    if re.search(r'[<>"\s\'=]', link):
        return False
    return True

def decode_happ_link(happ_url):
    try:
        decoder_url = "https://happy-decoder.cc/"
        data = urllib.parse.urlencode({'url': happ_url}).encode('utf-8')
        
        req = urllib.request.Request(
            decoder_url,
            data=data,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        textarea_match = re.search(r'<textarea[^>]*>(.*?)</textarea>', html, re.DOTALL)
        if not textarea_match:
            return []
            
        search_space = clean_and_fix_link(textarea_match.group(1))
        pure_links = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', search_space)
        return [clean_and_fix_link(l) for l in pure_links if is_clean_link(clean_and_fix_link(l))]
    except:
        return []

def get_links_from_channel(ch_data):
    html = fetch_url(ch_data["url"])
    if not html:
        return []
        
    # Sınıf filtresini kaldırdık: Sayfanın TÜMÜNDE geçen linkleri ve href leri doğrudan topluyoruz
    href_links = re.findall(r'href="([^"]+)"', html)
    text_links = re.findall(r'(?:happ|vless|vmess|ss|trojan)://[^\s<>"\']+', html)
    
    all_found = href_links + text_links
    
    links = []
    for url in all_found:
        if len(links) >= ch_data["limit"]:
            break
            
        cleaned_url = clean_and_fix_link(url)
        
        # Telegram t.me yönlendirme linklerini atla
        if any(x in cleaned_url for x in ['t.me/s/', 't.me/iv', 't.me/share', 'telegram.dog']):
            continue
            
        if cleaned_url.startswith('happ://'):
            decoded_lines = decode_happ_link(cleaned_url)
            for line in decoded_lines:
                if len(links) >= ch_data["limit"]:
                    break
                fixed_line = clean_and_fix_link(line)
                if is_clean_link(fixed_line) and fixed_line not in links:
                    links.append(fixed_line)
        else:
            if is_clean_link(cleaned_url) and cleaned_url not in links:
                links.append(cleaned_url)
                    
    return links[:ch_data["limit"]]

def main():
    # 1. İlk 12 satırı kesinlikle koru
    header_lines = []
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "r", encoding="utf-8") as f:
                all_lines = f.read().splitlines()
                header_lines = all_lines[:12]
        except:
            pass

    # 2. Kanallardan taze linkleri global olarak topla
    final_pool = []
    for ch_name, data in CHANNELS.items():
        print(f"{ch_name} kanalının genel kaynağı taranıyor...")
        channel_links = get_links_from_channel(data)
        print(f"{ch_name} kanalından alınan temiz link sayısı: {len(channel_links)}")
        final_pool.extend(channel_links)
        
    if len(final_pool) < 3:
        print("HATA: Yeterli link bulunamadı, dosya korunuyor.")
        return

    # 3. Estetik ülke isimleriyle etiketle
    formatted_links = []
    for i, link in enumerate(final_pool):
        clean_link = link.split('#')[0]
        country = COUNTRY_NAMES[i % len(COUNTRY_NAMES)]
        formatted_links.append(f"{clean_link}#{urllib.parse.quote(country)}")

    # 4. İlk 12 satır başlık + altlarına yeni linkler
    combined_content = header_lines + formatted_links

    tmp_file = "KODLARY.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    os.replace(tmp_file, "KODLARY")
    print("BAŞARILI: Global tarama tamamlandı, liste güncellendi!")

if __name__ == "__main__":
    main()
