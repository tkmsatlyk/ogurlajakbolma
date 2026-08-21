import re
import os
import urllib.request
from playwright.sync_api import sync_playwright

def main():
    print("--- Başlatıldı ---")
    
    # 1. Adım: Kanalı çek
    try:
        req = urllib.request.Request("https://t.me/s/happvpn", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
    except: return

    happ_links = re.findall(r'happ://[^\s<>"\']+', content)
    if not happ_links: return
    latest_happ = happ_links[-1].replace('&amp;', '&').strip()
    
    print(f"Çözülecek link: {latest_happ}")

    # 2. Adım: Decryptor'a git (Dış siteyi kullanıyoruz, yerel karmaşadan kurtulduk)
    vpn_nodes = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://happy-decoder.cc/")
            
            # Input'a yaz ve çöz
            page.fill("textarea, input[type='text']", latest_happ)
            page.press("textarea, input[type='text']", "Enter")
            page.wait_for_timeout(5000)
            
            content = page.content()
            browser.close()
            
            # Linkleri al
            vpn_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', content)
    except: pass

    if vpn_nodes:
        with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(list(dict.fromkeys(vpn_nodes))))
        print("İşlem tamam, dosya yazıldı.")

if __name__ == "__main__":
    main()
