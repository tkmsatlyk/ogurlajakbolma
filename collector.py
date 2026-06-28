import urllib.request
import re

# RSS.app'den aldığın o altın anahtar burada:
RSS_URL = "https://rss.app/feeds/SntEdwZf2uMuNxOn.xml"

def main():
    try:
        req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            rss_content = response.read().decode('utf-8', errors='ignore')
            
            # Kanal mesajındaki Happ:// kodunu avlayan regex:
            match = re.search(r'happ://crypt5/[^\s"\']+', rss_content)
            
            if match:
                clean_code = match.group(0)
                # Senin markanla paketleme (Ares ismini tamamen sildik):
                final_output = f"{clean_code}#《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》"
                
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(final_output)
                print(f"[+] Yeni kod başarıyla avlandı: {clean_code[:20]}...")
            else:
                print("[-] Kanalda yeni kod bulunamadı, sistem beklemede.")
                
    except Exception as e:
        print(f"[-] Hata oluştu: {e}")

if __name__ == "__main__":
    main()
