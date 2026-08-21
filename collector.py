import urllib.request
import urllib.parse
import re
import os
import socket
import time
import random
import http.client

# KOTALAR: 8 + 6 + 6 + 5 = 25 Link
CHANNELS = {
    "happvpn": {"url": "https://t.me/s/happvpn", "limit": 8, "max_ms": 1500},
    "ares_happ": {"url": "https://t.me/s/ares_happ", "limit": 6, "max_ms": 1500},
    "Richman_vpns": {"url": "https://t.me/s/Richman_vpns", "limit": 6, "max_ms": 1500},
    "LonUp_M": {"url": "https://t.me/s/LonUp_M", "limit": 5, "max_ms": 700}
}

COUNTRY_NAMES = [
    "🇩🇪 𝐆𝐞𝐫𝐦𝐚𝐧𝐲", "🇳🇱 𝐍𝐞𝐭𝐡𝐞𝐫𝐥𝐚𝐧𝐝𝐬", "🇺🇸 𝐔𝐧𝐢𝐭𝐞𝐝 𝐒𝐭𝐚𝐭𝐞𝐬", "🇬🇧 𝐔𝐧𝐢𝐭𝐞𝐝 𝐊𝐢𝐧𝐠𝐝𝐨𝐦",
    "🇫🇷 🇫𝐫𝐚𝐧𝐜𝐞", "🇹🇷 𝐓𝐮𝐫𝐤𝐞𝐲", "🇷🇺 🇷𝐮𝐬𝐬𝐢𝐚", "🇷🇴 𝐑𝐨𝐦𝐚𝐧𝐢𝐚",
    "🇨🇭 𝐒𝐰𝐢𝐭𝐳𝐞𝐫𝐥𝐚𝐧𝐝", "🇸🇪 𝐒𝐰𝐞𝐝𝐞𝐧", "🇵🇱 𝐏𝐨𝐥𝐚𝐧𝐝", "🇮🇹 𝐈𝐭𝐚𝐥𝐲",
    "🇧🇬 𝐁𝐮𝐥𝐠𝐚𝐫𝐢𝐚", "🇦🇹 🇦𝐮𝐬𝐭𝐫𝐢𝐚", "🇨🇦 𝐊𝐚𝐧𝐚𝐝𝐚", "🇸🇬 𝐒𝐢𝐧𝐠𝐚𝐩𝐨𝐫𝐞",
    "🇯🇵 𝐉𝐚𝐩𝐚𝐧", "🇰🇷 𝐒𝐨𝐮𝐭𝐡 𝐊𝐨𝐫𝐞𝐚", "🇦🇪 𝐔𝐧𝐢𝐭𝐞𝐝 𝐀𝐫𝐚𝐛 𝐄𝐦𝐢𝐫𝐚𝐭𝐞𝐬",
    "🇰🇿 𝐊𝐚𝐳𝐚𝐤𝐡𝐬𝐭𝐚𝐧", "🇦🇺 𝐀𝐮𝐬𝐭𝐫𝐚𝐥𝐢𝐚", "🇭🇰 𝐇𝐨𝐧𝐠 𝐊𝐨𝐧𝐠", "🇳🇴 🇳𝐨𝐫𝐰𝐚𝐲",
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
    except Exception as e:
        print(f"Bağlantı hatası ({url}): {e}")
        return ''

def clean_and_fix_link(link):
    return link.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'").strip()

def decode_happ_link(happ_url):
    try:
        decoder_api = f"https://happy-decoder.cc/?url={urllib.parse.quote(happ_url)}"
        html = fetch_url(decoder_api)
        textarea_match = re.search(r'<textarea[^>]*>(.*?)</textarea>', html, re.DOTALL)
        search_space = textarea_match.group(1) if textarea_match else html
        search_space = clean_and_fix_link(search_space)
        pure_links = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', search_space)
        return [clean_and_fix_link(l) for l in pure_links]
    except:
        return []

def test_latency(host, port):
    try:
        start = time.time()
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
        return ((time.time() - start) * 1000 * 7.5) + random.uniform(80, 250)
    except:
        return 9999

def get_links_from_channel(ch_data):
    html = fetch_url(ch_data["url"])
    if not html:
        return []
        
    # Tüm mesaj bloklarını al ve TERSE ÇEVİR (En son/en yeni paylaşılan mesaj en başta olsun)
    message_blocks = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
    if not message_blocks:
        return []
        
    latest_blocks = message_blocks[::-1] # En yeni paylaşımdan eskiye doğru tara
    
    links = []
    for block in latest_blocks:
        if len(links) >= ch_data["limit"]:
            break
        
        clean_block = re.sub(r'<br\s*/?>', '\n', block)
        clean_block = re.sub(r'<[^>]+>', '', clean_block)
        clean_block = clean_and_fix_link(clean_block)
        
        found = re.findall(r'(?:happ|vless|vmess|ss|trojan)://[^\s<>"\']+', clean_block)
        
        for url in found:
            if len(links) >= ch_data["limit"]:
                break
            cleaned_url = clean_and_fix_link(url)
            
            if cleaned_url.startswith('happ://'):
                decoded_lines = decode_happ_link(cleaned_url)
                for line in decoded_lines:
                    if len(links) >= ch_data["limit"]:
                        break
                    fixed_line = clean_and_fix_link(line)
                    try:
                        host_port = fixed_line.split('://', 1)[1].split('@')[-1].split('?')[0].split('#')[0]
                        host, port = host_port.rsplit(':', 1)
                        if test_latency(host, port.split('/')[0]) <= ch_data["max_ms"]:
                            if fixed_line not in links:
                                links.append(fixed_line)
                    except:
                        if fixed_line not in links:
                            links.append(fixed_line)
            else:
                try:
                    host_port = cleaned_url.split('://', 1)[1].split('@')[-1].split('?')[0].split('#')[0]
                    host, port = host_port.rsplit(':', 1)
                    if test_latency(host, port.split('/')[0]) <= ch_data["max_ms"]:
                        if cleaned_url not in links:
                            links.append(cleaned_url)
                except:
                    if cleaned_url not in links:
                        links.append(cleaned_url)
                        
    return links[:ch_data["limit"]]

def main():
    # 1. İlk 12 satırı kesinlikle koru ve dokunma
    header_lines = []
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "r", encoding="utf-8") as f:
                all_lines = f.read().splitlines()
                header_lines = all_lines[:12]
        except:
            pass

    # 2. Kanallardaki en son paylaşımları tara, test et ve topla
    final_pool = []
    for ch_name, data in CHANNELS.items():
        print(f"{ch_name} kanalının en son paylaşımları taranıyor...")
        channel_links = get_links_from_channel(data)
        print(f"{ch_name} kanalından alınan çalışan link: {len(channel_links)}")
        final_pool.extend(channel_links)
        
    if len(final_pool) < 3:
        print("HATA: Yeterli link bulunamadı, dosya korunuyor.")
        return

    # 3. İsimleri estetik İngilizce ülke isimleriyle değiştir
    formatted_links = []
    for i, link in enumerate(final_pool):
        clean_link = link.split('#')[0]
        country = COUNTRY_NAMES[i % len(COUNTRY_NAMES)]
        formatted_links.append(f"{clean_link}#{urllib.parse.quote(country)}")

    # 4. İlk 12 satır başlık + altlarına test edilmiş yeni linkler
    combined_content = header_lines + formatted_links

    tmp_file = "KODLARY.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    os.replace(tmp_file, "KODLARY")
    print("BAŞARILI: En son paylaşımlar alındı, test edildi ve KODLARY güncellendi!")

if __name__ == "__main__":
    main()
