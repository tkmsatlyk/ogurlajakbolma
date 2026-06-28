import urllib.request
import re
import base64

RSS_URL = "https://rss.app/feeds/SntEdwZf2uMuNxOn.xml"

def main():
    try:
        # RSS'den veriyi al
        req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            rss_content = response.read().decode('utf-8', errors='ignore')
            
            # Ares'in uzun kodunu yakala
            match = re.search(r'happ://crypt5/([A-Za-z0-9+/=]+)', rss_content)
            
            if match:
                # Kodun ham halini al
                clean_code = match.group(0)
                
                # UYGULAMAYA FORMAT VER: 
                # Happ uygulamaları genellikle başında #profile-title ve config gerektirir.
                # İşte olması gereken format:
                full_config = f"""#profile-title: 《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》
#profile-update-interval: 0
#subscription-userinfo: upload=0; download=0; total=53687091200; expire=1924992000

{clean_code}"""
                
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(full_config)
                print("[+] Format hatası giderildi, dosya yapılandırıldı.")
            else:
                print("[-] Kanalda geçerli kod bulunamadı.")
                
    except Exception as e:
        print(f"[-] Hata: {e}")

if __name__ == "__main__":
    main()
