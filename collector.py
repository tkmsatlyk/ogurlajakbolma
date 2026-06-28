import urllib.request
import re

# RSS.app'den aldığın link buraya:
RSS_URL = "https://rss.app/feeds/SntEdwZf2uMuNxOn.xml"

# Happ uygulamasının "doğru" kabul ettiği abonelik başlığı
HEADER = """#profile-title: 《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》
#profile-update-interval: 0
#subscription-userinfo: upload=0; download=0; total=53687091200; expire=1924992000
"""

def main():
    try:
        req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            rss_content = response.read().decode('utf-8', errors='ignore')
            
            match = re.search(r'happ://crypt5/[^\s"\']+', rss_content)
            
            if match:
                clean_code = match.group(0)
                # İsimlendirme: Kodun yanına değil, başlık kısmına ekledik
                final_output = HEADER + clean_code
                
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(final_output)
                print("[+] Sistem dosyası mükemmel formata getirildi!")
            else:
                print("[-] Kanalda kod bulunamadı.")
                
    except Exception as e:
        print(f"[-] Hata: {e}")

if __name__ == "__main__":
    main()
