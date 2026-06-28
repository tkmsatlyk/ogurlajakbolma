import urllib.request
import re

RSS_URL = "https://rss.app/feeds/SntEdwZf2uMuNxOn.xml"

def main():
    try:
        req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            rss_content = response.read().decode('utf-8', errors='ignore')
            
            # Ares'in kanalındaki o uzun kod dizisini tam yakalayan regex
            # Bu regex, 'happ://crypt5/' ile başlayan ve boşluğa kadar giden her şeyi alır
            match = re.search(r'happ://crypt5/[A-Za-z0-9+/=]+', rss_content)
            
            if match:
                full_code = match.group(0) # Kodun kendisi
                
                # Uygulamanın istediği tam format:
                final_content = f"""#profile-title: 《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=53687091200; expire=1924992000

{full_code}"""
                
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(final_content)
                print("[+] Kod başarıyla avlandı ve dosyaya yazıldı!")
            else:
                print("[-] HATA: Kod bulunamadı! RSS içeriği kontrol edilmeli.")
                
    except Exception as e:
        print(f"[-] Hata: {e}")

if __name__ == "__main__":
    main()
