import re
import os
import urllib.request
import zipfile
import shutil
import subprocess
import time
import socket
from playwright.sync_api import sync_playwright

custom_names = [
    "🔥 Pro-VPN-01",
    "⚡ Pro-VPN-02",
    "🚀 Pro-VPN-03",
    "💎 Pro-VPN-04",
    "🌐 Pro-VPN-05",
    "⚡ Pro-VPN-06",
    "🔥 Pro-VPN-07",
    "🚀 Pro-VPN-08",
    "💎 Pro-VPN-09",
    "🌐 Pro-VPN-10"
]

def setup_decryptor():
    zip_url = "https://github.com/LeeeeT/happ-decryptor/archive/refs/heads/main.zip"
    zip_path = "decryptor.zip"
    print("Decrypter deposu ZIP olarak indiriliyor...")
    urllib.request.urlretrieve(zip_url, zip_path)
    
    if os.path.exists("happ-decryptor"):
        shutil.rmtree("happ-decryptor", ignore_errors=True)
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("temp_extract")
        
    extracted_folder = os.path.join("temp_extract", "happ-decryptor-main")
    shutil.move(extracted_folder, "happ-decryptor")
    shutil.rmtree("temp_extract", ignore_errors=True)
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    print("NPM paketleri yükleniyor ve proje derleniyor...")
    os.chdir("happ-decryptor")
    subprocess.run(["npm", "install"], check=True)
    subprocess.run(["npm", "run", "build"], check=True)
    
    print("Yerel preview sunucusu başlatılıyor...")
    server_process = subprocess.Popen(["npm", "run", "preview"])
    os.chdir("..")
    time.sleep(5)
    return server_process

def ping_node(node_url):
    try:
        match = re.search(r'@[^:]+:(\d+)', node_url) or re.search(r'//[^:]+:(\d+)', node_url)
        # Basit host ve port çıkarma
        parsed = urllib.parse.urlparse(node_url)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return 9999
        
        start = time.time()
        with socket.create_connection((host, port), timeout=1.5):
            latency = int((time.time() - start) * 1000)
            return latency
    except:
        return 9999

def fetch_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def main():
    server_process = None
    try:
        server_process = setup_decryptor()
        
        print("--- Telegram Kanalı Taranıyor ---")
        try:
            tg_html = fetch_url("https://t.me/s/happvpn")
        except Exception as e:
            print(f"Telegram bağlantı hatası: {e}")
            return

        happ_matches = re.findall(r'happ://[^\s<>"\']+', tg_html)
        if not happ_matches:
            print("Hiç happ linki bulunamadı.")
            return

        latest_happ = happ_matches[-1].replace('&amp;', '&').strip()
        print(f"Bulunan son happ link: {latest_happ}")

        print("Yerel Decryptor ile şifre çözülüyor...")
        decoder_url = "http://localhost:4173/"
        decoded_content = ""
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            page = browser.new_page()
            page.goto(decoder_url, timeout=30000)
            
            input_selector = "textarea, input[type='text'], input"
            page.wait_for_selector(input_selector, timeout=10000)
            page.fill(input_selector, latest_happ)
            
            try:
                page.click("button, input[type='submit']", timeout=5000)
            except:
                page.press(input_selector, "Enter")
            
            page.wait_for_timeout(5000)
            decoded_content = page.content()
            browser.close()

        # Çözülen veriden https linkini yakala
        https_matches = re.findall(r'https?://[^\s<>"\']+', decoded_content)
        target_url = None
        for u in https_matches:
            if "t.me" not in u and "github" not in u and "localhost" not in u:
                target_url = u
                break
        
        # Eğer doğrudan node çıktıysa onları al, çıkmadıysa https linkini çek
        raw_configs = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', decoded_content)
        
        if not raw_configs and target_url:
            print(f"Bulunan abonelik URL'si: {target_url}")
            try:
                sub_content = fetch_url(target_url)
                # Base64 decode denemesi
                try:
                    import base64
                    decoded_sub = base64.b64decode(sub_content.strip()).decode('utf-8')
                    raw_configs = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', decoded_sub)
                except:
                    raw_configs = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', sub_content)
            except Exception as e:
                print(f"Abonelik URL çekilemedi: {e}")

        print(f"Toplam ham node sayısı: {len(raw_configs)}")
        if not raw_configs:
            print("Hiç node bulunamadı.")
            return

        print("Ping testleri başlatılıyor (< 1500ms)...")
        tested_nodes = []
        for config in raw_configs:
            ping = ping_node(config)
            if ping < 1500:
                tested_nodes.append((ping, config))
                print(f"[PASS] Ping: {ping}ms")

        # Pinge göre sırala
        tested_nodes.sort(key=lambda x: x[0])

        final_links = []
        for index, (ping, config) in enumerate(tested_nodes[:10]):
            clean_config = config.split('#')[0]
            assigned_name = customNames[index] if index < len(customNames) else f"Pro-Node-{index + 1}"
            import urllib.parse
            renamed_config = f"{clean_config}#{urllib.parse.quote(assigned_name)}"
            final_links.append(renamed_config)

        if final_links:
            with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(final_links))
            print(f"BAŞARILI: Toplam {len(final_links)} adet optimize node dosyaya yazıldı.")
        else:
            print("1500ms altında uygun node bulunamadı.")

    finally:
        if server_process:
            server_process.terminate()

if __name__ == "__main__":
    main()
