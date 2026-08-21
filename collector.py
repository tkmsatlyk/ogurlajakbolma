import re
import os
import urllib.request
from playwright.sync_api import sync_playwright

def main():
    print("--- Yerel Sunucu Tabanlı Kesin Çözüm Başlatıldı ---")
    
    channel_url = "https://t.me/s/happvpn"
    
    # 1. Adım: Telegram kanalından en taze happ:// crypt kodunu çek
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
    
    # Yerel Vite preview sunucusunun adresi
    decoder_url = "http://localhost:4173/"

    print("Yerel Sunucu üzerinden Playwright ile Şifre Çözülüyor...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            page = browser.new_page()
            
            # Yerel Node sunucusuna bağlanıyoruz
            page.goto(decoder_url, timeout=30000)
            
            # Input / Textarea alanına crypt kodunu yaz
            input_selector = "textarea, input[type='text'], input"
            page.wait_for_selector(input_selector, timeout=10000)
            page.fill(input_selector, latest_happ)
            
            # Çöz butonuna tıkla
            try:
                page.click("button, input[type='submit']", timeout=5000)
            except:
                page.press(input_selector, "Enter")
            
            # Şifrenin çözülmesi için bekleme payı
            page.wait_for_timeout(5000)
            
            content = page.content()
            browser.close()
            
            # Node'ları ayıkla
            found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', content)
            vpn_nodes.extend(found_nodes)
            
            textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', content, re.DOTALL | re.IGNORECASE)
            for ta in textareas:
                ta_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', ta)
                vpn_nodes.extend(ta_nodes)

    except Exception as e:
        print(f"Yerel Çözüm Hatası: {e}")
        return

    if not vpn_nodes:
        print("Kritik Hata: Yerel araç ile de node'lar çıkarılamadı.")
        return

    vpn_nodes = list(dict.fromkeys(vpn_nodes))
    print(f"Toplam {len(vpn_nodes)} adet VPN linki başarıyla toplandı.")

    # KODLARY dosyasına KESİNLİKLE dokunulmuyor, sadece Toplanan_linkler.txt güncelleniyor
    try:
        with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(vpn_nodes))
        print("İşlem başarıyla tamamlandı! Sadece 'Toplanan_linkler.txt' güncellendi.")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
