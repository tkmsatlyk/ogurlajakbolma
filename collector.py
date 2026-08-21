import re, urllib.request
from playwright.sync_api import sync_playwright

def main():
    try:
        # Telegram'dan al
        req = urllib.request.Request("https://t.me/s/happvpn", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp: content = resp.read().decode('utf-8', errors='ignore')
        
        happ_links = re.findall(r'happ://[^\s<>"\']+', content)
        if not happ_links: return
        latest = happ_links[-1].replace('&amp;', '&').strip()
        
        # Çöz
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://happy-decoder.cc/")
            page.fill("textarea, input[type='text']", latest)
            page.press("textarea, input[type='text']", "Enter")
            page.wait_for_timeout(5000)
            content = page.content()
            browser.close()
            
        nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', content)
        if nodes:
            with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(list(dict.fromkeys(nodes))))
            print("Linkler yazıldı.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__": main()
