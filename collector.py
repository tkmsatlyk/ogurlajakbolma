import re
import os
import urllib.request
import zipfile
import shutil
import subprocess
import time
from playwright.sync_api import sync_playwright

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
    time.sleep(5)  # Sunucunun ayağa kalkması için bekleme
    return server_process

def main():
    server_process = None
    try:
        server_process = setup_decryptor()
        
        channel_url = "https://t.me/s/happvpn"
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

        vpn_nodes = []
        decoder_url = "http://localhost:4173/"

        print("Playwright ile şifre çözülüyor...")
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
            content = page.content()
            browser.close()
            
            found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', content)
            vpn_nodes.extend(found_nodes)
            
            textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', content, re.DOTALL | re.IGNORECASE)
            for ta in textareas:
                ta_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', ta)
                vpn_nodes.extend(ta_nodes)

        if not vpn_nodes:
            print("Kritik Hata: Node'lar çıkarılamadı.")
            return

        vpn_nodes = list(dict.fromkeys(vpn_nodes))
        print(f"Toplam {len(vpn_nodes)} adet VPN linki başarıyla toplandı.")

        try:
            with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(vpn_nodes))
            print("İşlem başarıyla tamamlandı! Sadece 'Toplanan_linkler.txt' güncellendi.")
        except Exception as e:
            print(f"Dosya yazma hatası: {e}")

    finally:
        if server_process:
            server_process.terminate()

if __name__ == "__main__":
    main()
