import urllib.request
import urllib.parse
import re
import socket
import time
import random
import os
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
    "🇫🇷 𝐅𝐫𝐚𝐧𝐜𝐞", "🇹🇷 𝐓𝐮𝐫𝐤𝐞𝐲", "🇷🇺 🇷𝐮𝐬𝐬𝐢𝐚", "🇷🇴 𝐑𝐨𝐦𝐚𝐧𝐢𝐚",
    "🇨🇭 𝐒𝐰𝐢𝐭𝐳𝐞𝐫𝐥𝐚𝐧𝐝", "🇸🇪 𝐒𝐰𝐞𝐝𝐞𝐧", "🇵🇱 𝐏𝐨𝐥𝐚𝐧𝐝", "🇮🇹 𝐈𝐭𝐚𝐥𝐲",
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Encoding': 'identity'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except http.client.IncompleteRead as e:
        return e.partial.decode('utf-8', errors='ignore')
    except: return ''

def decode_happ_link(happ_url):
    try:
        decoder_api = f"https://happy-decoder.cc/?url={urllib.parse.quote(happ_url)}"
        html = fetch_url(decoder_api)
        # HTML içinden sadece GERÇEK proxy linklerini ayıkla (HTML etiketlerini tamamen yok say)
        pure_links = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', html)
        return pure_links
    except: return []

def test_latency(host, port):
    try:
        start = time.time()
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
        return ((time.time() - start) * 1000 * 7.5) + random.uniform(80, 250)
    except: return 9999

def get_links_from_channel(ch_data):
    html = fetch_url(ch_data["url"])
    if not html: return []
        
    all_raw = re.findall(r'(?:happ|vless|vmess|ss|trojan)://[^\s<>"]+', html)
    links = []
    for url in all_raw:
        if len(links) >= ch_data["limit"]: break
        if url.startswith('happ://'):
            decoded_lines = decode_happ_link(url)
            for line in decoded_lines:
                if len(links) >= ch_data["limit"]: break
                try:
                    host_port = line.split('://', 1)[1].split('@')[-1].split('?')[0].split('#')[0]
                    host, port = host_port.rsplit(':', 1)
                    if test_latency(host, port.split('/')[0]) <= ch_data["max_ms"]: links.append(line)
                except: links.append(line)
        else:
            try:
                host_port = url.split('://', 1)[1].split('@')[-1].split('?')[0].split('#')[0]
                host, port = host_port.rsplit(':', 1)
                if test_latency(host, port.split('/')[0]) <= ch_data["max_ms"]: links.append(url)
            except: links.append(url)
    return links[:ch_data["limit"]]

def main():
    final_pool = []
    for ch_name, data in CHANNELS.items():
        final_pool.extend(get_links_from_channel(data))
        
    output = [f"{link.split('#')[0]}#{urllib.parse.quote(COUNTRY_NAMES[i % len(COUNTRY_NAMES)])}" for i, link in enumerate(final_pool)]
    
    if len(output) < 5: 
        print(f"HATA: Çok az link bulundu ({len(output)} adet). Dosya korunuyor.")
        return

    # İlk 12 satırı koruma
    header_lines = []
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "r", encoding="utf-8") as f:
                all_old_lines = [line.strip() for line in f if line.strip()]
                header_lines = all_old_lines[:12]
        except: pass

    combined_content = header_lines + output

    tmp_file = "KODLARY.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    os.replace(tmp_file, "KODLARY")
    print(f"BAŞARILI: KODLARY temizlendi ve güncellendi.")

if __name__ == "__main__":
    main()
