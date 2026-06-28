import urllib.request
import re

def main():
    print("Kanala bağlanılıyor...")
    url = "https://t.me/s/aresvpn_2"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Kanalda 'happ://' ile başlayan ne varsa bul
            matches = re.findall(r'happ://[^\s<>"]+', html)
            
            if not matches:
                print("HATA: Kanalda 'happ://' ile başlayan hiçbir şey bulunamadı!")
                print("Sayfa içeriğinin ilk 500 karakteri:")
                print(html[:500]) # Kanalda ne gördüğünü buraya dökecek
                return
            
            print(f"Bulunan tüm linkler: {matches}")
            
            # Link bulunduysa dosyaya yaz
            latest_url = matches[-1]
            with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                f.write(latest_url)
            print(f"Dosyaya yazıldı: {latest_url}")
            
    except Exception as e:
        print(f"KRİTİK HATA: {e}")

if __name__ == "__main__":
    main()
