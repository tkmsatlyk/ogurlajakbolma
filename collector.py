import urllib.request
import urllib.parse
import json
import re
import socket
import time
import random
import os

# KOTALAR: 8 + 6 + 6 + 5 = 25 Link
CHANNELS = {
    "happvpn": {"url": "https://t.me/s/happvpn", "limit": 8, "max_ms": 1500},
    "ares_happ": {"url": "https://t.me/s/ares_happ", "limit": 6, "max_ms": 1500},
    "Richman_vpns": {"url": "https://t.me/s/Richman_vpns", "limit": 6, "max_ms": 1500},
    "LonUp_M": {"url": "https://t.me/s/LonUp_M", "limit": 5, "max_ms": 700}
}

# Tamamen İngilizce ve Times New Roman / Serif Estetik Fontlu Ülke İsimleri
COUNTRY_NAMES = [
    "🇩🇪 𝐆𝐞𝐫𝐦𝐚𝐧𝐲", "🇳🇱 𝐍𝐞𝐭𝐡𝐞𝐫𝐥𝐚𝐧𝐝𝐬", "🇺🇸 𝐔𝐧𝐢𝐭𝐞𝐝 𝐒𝐭𝐚𝐭𝐞𝐬", "🇬🇧 𝐔𝐧𝐢𝐭𝐞𝐝 𝐊𝐢𝐧𝐠𝐝𝐨𝐦",
    "🇫🇷 🇫𝐫𝐚𝐧𝐜𝐞", "🇹🇷 𝐓𝐮𝐫𝐤𝐞𝐲", "🇷🇺 🇷𝐮𝐬𝐬𝐢𝐚", "🇷🇴 🇷𝐨𝐦𝐚𝐧𝐢𝐚",
    "🇨🇭 𝐒𝐰𝐢𝐭𝐳𝐞𝐫𝐥𝐚𝐧𝐝", "🇸🇪 🇸𝐰𝐞𝐝𝐞𝐧", "🇵🇱 𝐏𝐨𝐥𝐚𝐧𝐝", "🇮🇹 🇮𝐭𝐚𝐥𝐲",
    "🇧🇬 𝐁𝐮𝐥𝐠𝐚𝐫𝐢𝐚", "🇦🇹 🇦𝐮𝐬𝐭𝐫𝐢𝐚", "🇨🇦 𝐂𝐚𝐧𝐚𝐝𝐚", "🇸🇬 𝐒𝐢𝐧𝐠𝐚𝐩𝐨𝐫𝐞",
    "🇯🇵 𝐉𝐚𝐩𝐚𝐧", "🇰🇷 𝐒𝐨𝐮𝐭𝐡 𝐊𝐨𝐫𝐞𝐚", "🇦🇪 𝐔𝐧𝐢𝐭𝐞𝐝 𝐀𝐫𝐚𝐛 𝐄𝐦𝐢𝐫𝐚𝐭𝐞𝐬",
    "🇰🇿 𝐊𝐚𝐳𝐚𝐤𝐡𝐬𝐭𝐚𝐧", "🇦🇺 🇦𝐮𝐬𝐭𝐫𝐚𝐥𝐢𝐚", "🇭🇰 𝐇𝐨𝐧𝐠 𝐊𝐨𝐧𝐠", "🇳🇴 🇳𝐨𝐫𝐰𝐚𝐲",
    "🇵🇹 𝐏𝐨𝐫𝐭𝐮𝐠𝐚𝐥", "🇮🇳 🇮𝐧𝐝𝐢𝐚"
]

def fetch_url(url):
    try:
        proxy_api = f"https://api.allorigins.win/get?url={urllib.parse.quote(url)}"
        req = urllib.request.Request(proxy_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('contents', '')
    except: return ''

def decode_happ_link(happ_url):
    try:
        decoder_api = f"https://happy-decoder.cc/?url={urllib.parse.quote(happ_url)}"
        return fetch_url(decoder_api)
    except: return ''

def test_latency(host, port):
    try:
        start = time.time()
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
        return ((time.time() - start) * 1000 * 7.5) + random.uniform(80, 250)
    except: return 9999

def get_links_from_channel(ch_data):
    html = fetch_url(ch_data["url"])
    all_raw = re.findall(r'(?:happ|vless|vmess|ss|trojan)://[^\s<>"]+', html)
    links = []
    for url in all_raw:
        if len(links) >= ch_data["limit"]: break
        if url.startswith('happ://'):
            content = decode_happ_link(url)
            lines = [l.strip() for l in content.splitlines() if '://' in l]
        else: lines = [url]
        for line in lines:
            try:
                host_port = line.split('://', 1)[1].split('@')[-1].split('?')[0].split('#')[0]
                host, port = host_port.rsplit(':', 1)
                if test_latency(host, port.split('/')[0]) <= ch_data["max_ms"]: links.append(line)
            except: links.append(line)
    return links[:ch_data["limit"]]

def main():
    final_pool = []
    for ch_name, data in CHANNELS.items():
        final_pool.extend(get_links_from_channel(data))
        
    output = [f"{link.split('#')[0]}#{urllib.parse.quote(COUNTRY_NAMES[i % len(COUNTRY_NAMES)])}" for i, link in enumerate(final_pool)]
    
    # Güvenlik sigortası: 20'den az link varsa sistemi durdur, eski dosyayı koru
    if len(output) < 20: 
        print(f"HATA: Sadece {len(output)} link bulundu, dosya güvenliği için güncelleme yapılmadı.")
        return

    # 1. MEVCUT KODLARY DOSYASINDAN İLK 12 SATIRI OKU VE KORU
    header_lines = []
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "r", encoding="utf-8") as f:
                all_old_lines = [line.strip() for line in f if line.strip()]
                header_lines = all_old_lines[:12] # İlk 12 satıra dokunulmaz!
        except:
            pass

    # 2. İLK 12 SATIR İLE YENİ GELEN İNGİLİZCE İSİMLİ LİNKLERİ BİRLEŞTİR
    combined_content = header_lines + output

    # 3. GÜVENLİ YAZMA (TEMP DOSYASI İLE)
    tmp_file = "KODLARY.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    os.replace(tmp_file, "KODLARY")
    print(f"Başarıyla ilk {len(header_lines)} satır korundu, altına İngilizce isimli linkler eklendi.")

if __name__ == "__main__":
    main()
