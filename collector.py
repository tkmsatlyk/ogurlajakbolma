import urllib.request
import urllib.parse
import re
import os

try:
    from curl_cffi import requests as c_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

CHANNELS = {
    "happvpn": {"url": "https://t.me/s/happvpn", "limit": 10},
    "ares_happ": {"url": "https://t.me/s/ares_happ", "limit": 15}
}

COUNTRY_NAMES = [
    "🇩🇪 𝐆𝐞𝐫𝐦𝐚𝐧𝐲", "🇳🇱 𝐍𝐞𝐭𝐡𝐞𝐫𝐥𝐚𝐧𝐝𝐬", "🇺🇸 𝐔𝐧𝐢𝐭𝐞𝐝 𝐒𝐭𝐚𝐭𝐞𝐬", "🇬🇧 𝐔𝐧𝐢𝐭𝐞𝐝 𝐊𝐢𝐧𝐠𝐝𝐨𝐦",
    "🇫🇷 🇫𝐫𝐚𝐧𝐜𝐞", "🇹🇷 𝐓𝐮𝐫𝐤𝐞𝐲", "🇷🇺 🇷𝐮𝐬𝐬𝐢𝐚", "🇷🇴 𝐑𝐨𝐦𝐚𝐧𝐢𝐚",
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                'Accept-Encoding': 'identity'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[Net Error] {e}")
        return ''

def clean_link(link):
    return link.replace('&amp;', '&').replace('&quot;', '').strip()

def is_valid(link):
    if not any(link.startswith(p) for p in ['vless://', 'vmess://', 'ss://', 'trojan://']):
        return False
    if re.search(r'[<>"\s\']', link):
        return False
    return True

def decode_happ(happ_url):
    try:
        decoder_url = "https://happy-decoder.cc/"
        if HAS_CURL_CFFI:
            resp = c_requests.post(decoder_url, data={'url': happ_url}, impersonate="chrome120", timeout=15)
            html = resp.text
        else:
            data = urllib.parse.urlencode({'url': happ_url}).encode('utf-8')
            req = urllib.request.Request(decoder_url, data=data, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
        
        match = re.search(r'<textarea[^>]*>(.*?)</textarea>', html, re.DOTALL)
        if not match:
            return []
        found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', match.group(1))
        return [clean_link(l) for l in found if is_valid(clean_link(l))]
    except Exception as e:
        print(f"[Decoder Error] {e}")
        return []

def main():
    print("--- VPN Toplayıcı Başlatıldı ---")
    
    header_lines = []
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "r", encoding="utf-8") as f:
                header_lines = f.read().splitlines()[:12]
        except:
            pass

    final_pool = []
    
    # 1. ares_happ kanalından tam 15 tane al
    print("ares_happ taranıyor (Hedef: 15)...")
    html_ares = fetch_url(CHANNELS["ares_happ"]["url"])
    if html_ares:
        msg_blocks_ares = re.findall(r'<div[^>]*class="[^"]*tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html_ares, re.DOTALL)
        combined_ares = " ".join(msg_blocks_ares)
        clean_ares_text = re.sub(r'<[^>]+>', ' ', combined_ares)
        ares_links = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', clean_ares_text)
        for link in ares_links:
            if len(final_pool) >= CHANNELS["ares_happ"]["limit"]:
                break
            cl = clean_link(link)
            if is_valid(cl) and cl not in final_pool:
                final_pool.append(cl)
                print(f"[ares_happ] Eklendi. Toplam: {len(final_pool)}")

    # 2. happvpn kanalından son linki çöz ve 10 tane al
    print("happvpn taranıyor (Hedef: 10)...")
    html_happ = fetch_url(CHANNELS["happvpn"]["url"])
    if html_happ:
        msg_blocks_happ = re.findall(r'<div[^>]*class="[^"]*tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html_happ, re.DOTALL)
        combined_happ = " ".join(msg_blocks_happ)
        clean_happ_text = re.sub(r'<[^>]+>', ' ', combined_happ)
        happ_links = re.findall(r'happ://[^\s<>"\']+', clean_happ_text)
        if happ_links:
            latest = happ_links[-1]
            print(f"En son happ linki çözülüyor: {latest}")
            decoded = decode_happ(latest)
            happ_count = 0
            for link in decoded:
                if happ_count >= CHANNELS["happvpn"]["limit"]:
                    break
                cl = clean_link(link)
                if is_valid(cl) and cl not in final_pool:
                    final_pool.append(cl)
                    happ_count += 1
                    print(f"[happvpn] Eklendi. Happ Sayısı: {happ_count}")

    if not final_pool:
        print("Hiç node bulunamadı, mevcut dosya korunuyor.")
        return

    formatted = []
    for i, link in enumerate(final_pool):
        clean_l = link.split('#')[0]
        country = COUNTRY_NAMES[i % len(COUNTRY_NAMES)]
        formatted.append(f"{clean_l}#{urllib.parse.quote(country)}")

    combined_content = header_lines + formatted
    with open("KODLARY.tmp", "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    os.replace("KODLARY.tmp", "KODLARY")
    print(f"İşlem başarıyla tamamlandı! Toplam node: {len(final_pool)}")

if __name__ == "__main__":
    main()
