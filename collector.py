import urllib.request
import re
import time

RSS_URL = "https://rss.app/feeds/SntEdwZf2uMuNxOn.xml"

def main():
    try:
        cache_buster = f"{RSS_URL}?t={int(time.time())}"
        req = urllib.request.Request(cache_buster, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            rss_content = response.read().decode('utf-8', errors='ignore')
            
            # \S+ kullanarak boşluğa kadar ne var ne yok her şeyi alıyoruz (Linkin eksik kopyalanmasını önler)
            matches = re.findall(r'happ://crypt5/\S+', rss_content)
            
            if matches:
                latest_code = matches[-1]
                # Eğer linkin sonunda HTML veya gereksiz karakter kaldıysa temizle
                latest_code = latest_code.split('<')[0].split('"')[0]
                
                final_content = f"""#profile-title: 《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》
#profile-update-interval: 0
#subscription-userinfo: upload=0; download=0; total=53687091200; expire=1924992000

{latest_code}"""
                
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(final_content)
                print(f"[+] Basarili! Kod yazildi: {latest_code[:20]}...")
            else:
                print("[-] RSS icinde yeni kod bulunamadi.")
                
    except Exception as e:
        print(f"[-] Hata: {e}")

if __name__ == "__main__":
    main()
