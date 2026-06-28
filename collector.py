import urllib.request
import re

URL = "https://t.me/s/aresvpn_2"

def main():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(URL, headers=headers)
        
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8')
            
            # Regex ile sadece happ:// ile başlayan ve boşluğa/tırnağa kadar giden kodu al
            # Bu regex, isimleri, reklamları ve kanal yazılarını tamamen dışarıda bırakır.
            match = re.search(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            
            if match:
                clean_code = match.group(0)
                
                # Şimdi tertemiz bir şekilde dosyaya yazıyoruz
                final_content = f"""#profile-title: 《_🜲 VØRÐR 🔱 ELITE-VIP 🔱_》
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=53687091200; expire=1924992000

{clean_code}"""
                
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write(final_content)
                print(f"Başarıyla temizlendi ve yazıldı: {clean_code[:20]}...")
            else:
                print("Hata: Kod bulunamadı, kanal mesajları temizlenmiş olabilir.")
                
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
