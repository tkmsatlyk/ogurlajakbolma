import urllib.request
import re
import time # Zaman damgası ekledik

RSS_URL = "https://rss.app/feeds/SntEdwZf2uMuNxOn.xml"

def main():
    try:
        # RSS linkinin sonuna rastgele bir sayı ekleyerek 'cache'i kırıyoruz
        cache_buster = f"{RSS_URL}?t={int(time.time())}"
        
        req = urllib.request.Request(cache_buster, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            rss_content = response.read().decode('utf-8', errors='ignore')
            
            # Sadece son eklenen kodu değil, tüm sayfayı tara
            matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', rss_content)
            
            if matches:
                # En son eklenen kodu al
                latest_code = matches[-1] 
                
                final_content = f"""#profile-title: 《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》
#profile-update-interval: 0
#subscription-userinfo: upload=0; download=0; total=53687091200; expire=1924992000

{latest_code}"""
                
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(final_content)
                print(f"[+] Güncelleme tamamlandı: {latest_code[:15]}...")
            else:
                print("[-] Hata: RSS içinde kod bulunamadı!")
                
    except Exception as e:
        print(f"[-] Hata: {e}")

if __name__ == "__main__":
    main()
