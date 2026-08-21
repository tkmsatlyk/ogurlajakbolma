import re
import os
import urllib.request
from playwright.sync_api import sync_playwright

def main():
    print("--- Playwright Tarayıcı Tabanlı Kesin Çözüm Başlatıldı ---")
    
    channel_url = "https://t.me/s/happvpn"
    
    # 1. Adım: Kanaldan en taze happ:// crypt kodunu çek
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
    decoder_url = "https://happy-decoder.cc/"

    # 2. Adım: Playwright ile gerçek tarayıcı simülasyonu çalıştır
    print("Tarayıcı (Playwright) başlatılıyor...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Decoder sayfasına gidiliyor...")
            page.goto(decoder_url, timeout=30000)
            
            # Formdaki input / textarea alanını bul
            input_selector = "input[type='text'], textarea, input[name='url'], input"
            page.wait_for_selector(input_selector, timeout=10000)
            
            print("Crypt kod input alanına yazılıyor...")
            page.fill(input_selector, latest_happ)
            
            # Çöz / Gönder butonuna tıkla
            try:
                page.click("button[type='submit'], input[type='submit'], button", timeout=5000)
            except:
                page.press(input_selector, "Enter")
            
            print("Sonuçların yüklenmesi bekleniyor...")
            page.wait_for_timeout(6000) # Sayfanın JS ile çözmesi için bekleme payı
            
            content = page.content()
            browser.close()
            
            # A) Sayfadaki tüm vless/vmess node'larını çek
            found_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', content)
            vpn_nodes.extend(found_nodes)
            
            # B) Textarea içindeki çözülmüş verileri tara
            textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', content, re.DOTALL | re.IGNORECASE)
            for ta in textareas:
                ta_nodes = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"\']+', ta)
                vpn_nodes.extend(ta_nodes)

    except Exception as e:
        print(f"Tarayıcı Otomasyon Hatası: {e}")
        return

    if not vpn_nodes:
        print("Kritik Hata: Tarayıcı ile de node'lar çözülemedi.")
        return

    # Tekrarlanan linkleri temizle
    vpn_nodes = list(dict.fromkeys(vpn_nodes))
    print(f"Toplam {len(vpn_nodes)} adet VPN linki başarıyla toplandı.")

    # 3. Adım: KODLARY dosyasına KESİNLİKLE DOKUNMA, sadece Toplanan_linkler.txt dosyasına yaz
    try:
        with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(vpn_nodes))
        print("İşlem başarıyla tamamlandı! Linkler sadece 'Toplanan_linkler.txt' dosyasına yazıldı. KODLARY yerinde duruyor.")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

if __name__ == "__main__":
    main()
