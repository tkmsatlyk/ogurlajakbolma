import urllib.request
import urllib.parse
import re
import os
import socket
import time
import http.client

try:
    from curl_cffi import requests as c_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

CHANNELS = {
    "happvpn": {"url": "https://t.me/s/happvpn", "limit": 15},
    "LonUp_M": {"url": "https://t.me/s/LonUp_M", "limit": 15}
}

COUNTRY_NAMES = [
    "🇩🇪 𝐆𝐞𝐫𝐦𝐚𝐧𝐲", "🇳🇱 𝐍𝐞𝐭𝐡𝐞𝐫𝐥𝐚𝐧𝐝𝐬", "🇺🇸 𝐔𝐧𝐢𝐭𝐞𝐝 𝐒𝐭𝐚𝐭𝐞𝐬", "🇬🇧 𝐔𝐧𝐢𝐭𝐞𝐝 𝐊𝐢𝐧𝐠𝐝𝐨𝐦",
    "🇫🇷 🇫𝐫𝐚𝐧𝐜𝐞", "🇹🇷 🇹𝐮𝐫𝐤𝐞𝐲", "🇷🇺 🇷𝐮𝐬𝐬𝐢𝐚", "🇷🇴 🇷𝐨𝐦𝐚𝐧𝐢𝐚",
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
    except Exception as e:
        print(f"[Net Error] {url}: {e}")
        return ''

def clean_and_fix_link(link):
    return link.replace('&amp;', '&').replace('&quot;', '').replace('&#39;', '').strip()

def is_clean_link(link):
    if not any(link.startswith(p) for p in ['vless://', 'vmess://', 'ss://', 'trojan://']):
        return False
    if re.search(r'[<>"\s\'=]', link):
        return False
    return True

def extract_host_port(url):
    try:
        without_proto = url.split('://', 1)[1]
        base_part = without_proto.split('?')[0].split('#')[0]
        if '@' in base_part:
            host_port_part = base_part.rsplit('@', 1)[1]
        else:
            host_port_part = base_part
        if ':' in host_port_part:
            host, port = host_port_part.rsplit(':', 1)
            port = port.split('/')[0]
            return host, int(port)
    except:
        pass
    return None, None

def test_node_triple_ping(url):
    host, port = extract_host_port(url)
    if not host or not port:
        return False
    
    success_count = 0
    for _ in range(3):
        try:
            s = socket.create_connection((host, port), timeout=1.5)
            s.close()
            success_count += 1
        except:
            pass
        time.sleep(0.15)
        
    return success_count == 3

def decode_happ_link(happ_url):
    try:
        decoder_url = "https://happy-decoder.cc/"
        if HAS_CURL_CFFI:
            response = c_requests.post(decoder_url, data={'url': happ_url}, impersonate="chrome120", timeout=15)
            html = response.text
        else:
            data = urllib.parse.urlencode({'url': happ_url}).encode('utf-8')
            req = urllib.request.Request(
                decoder_url, data=data,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'https://happy-decoder.cc/'
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
    except Exception as e:
        print(f"[Decoder Error] {e}")
        return []

def get_links_from_channel(ch_data):
    html = fetch_url(ch_data["url"])
    if not html:
        return []
        
    message_blocks = re.findall(r'<div[^>]*class="[^"]*tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    combined_text = " ".join(message_blocks)
    clean_text = re.sub(r'<[^>]+>', ' ', combined_text)
    
    happ_links = re.findall(r'happ://[^\s<>"\']+', clean_text)
    direct_links = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', clean_text)
    
    links = []
    
    # happvpn için sadece EN SON (en güncel) paylaşılan happ:// linkini seçiyoruz
    if "happvpn" in ch_data["url"]:
        if happ_links:
            latest_happ = happ_links[-1]  # En sondaki/en yeni link
            print(f"[DEBUG] happvpn en son paylaşılan happ:// linki yakalandı: {latest_happ}")
            decoded_lines = decode_happ_link(latest_happ)
            for line in decoded_lines:
                if len(links) >= ch_data["limit"]:
                    break
                fixed_line = clean_and_fix_link(line)
                if is_clean_link(fixed_line) and fixed_line not in links:
                    if test_node_triple_ping(fixed_line):
                        links.append(fixed_line)
    else:
        # Diğer kanallar için standart tarama
        all_found = happ_links + direct_links
        for url in all_found:
            if len(links) >= ch_data["limit"]:
                break
            cleaned_url = clean_and_fix_link(url)
            if cleaned_url.startswith('happ://'):
                decoded_lines = decode_happ_link(cleaned_url)
                for line in decoded_lines:
                    if len(links) >= ch_data["limit"]:
                        break
                    fixed_line = clean_and_fix_link(line)
                    if is_clean_link(fixed_line) and fixed_line not in links:
                        if test_node_triple_ping(fixed_line):
                            links.append(fixed_line)
            else:
                if is_clean_link(cleaned_url) and cleaned_url not in links:
                    if test_node_triple_ping(cleaned_url):
                        links.append(cleaned_url)
                        
    return links[:ch_data["limit"]]

def main():
    print("--- [PRO] VPN Altyapı Güncelleyicisi Başlatıldı ---")
    
    header_lines = []
    if os.path.exists("KODLARY"):
        try:
            with open("KODLARY", "r", encoding="utf-8") as f:
                all_lines = f.read().splitlines()
                header_lines = all_lines[:12]
        except:
            pass

    final_pool = []
    for ch_name, data in CHANNELS.items():
        print(f"[*] {ch_name} taranıyor...")
        channel_links = get_links_from_channel(data)
        print(f"[+] {ch_name} aktif node sayısı: {len(channel_links)}")
        final_pool.extend(channel_links)
        
    if len(final_pool) < 2:
        print("[!] Kritik Uyarı: Yeterli node bulunamadı, mevcut KODLARY korundu.")
        return

    formatted_links = []
    for i, link in enumerate(final_pool):
        clean_link = link.split('#')[0]
        country = COUNTRY_NAMES[i % len(COUNTRY_NAMES)]
        formatted_links.append(f"{clean_link}#{urllib.parse.quote(country)}")

    combined_content = header_lines + formatted_links

    tmp_file = "KODLARY.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    os.replace(tmp_file, "KODLARY")
    print("--- [SUCCESS] KODLARY başarıyla güncellendi ve mühürlendi! ---")

if __name__ == "__main__":
    main()
