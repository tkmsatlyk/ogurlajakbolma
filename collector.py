import urllib.request
import base64
import re

# Ares'in kanalı
CHANNEL_URL = "https://t.me/s/aresvpn_2"

def main():
    try:
        # 1. AŞAMA: Kanalı tara ve en son paylaşılan linki bul
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(CHANNEL_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8')
            
            # Kanalda paylaşılan en son 'happ://' linkini bul
            matches = re.findall(r'happ://crypt5/[A-Za-z0-9+/=]+', html)
            if not matches:
                print("[-] Kanalda şu an yeni kod yok.")
                return
            
            latest_subscription_url = matches[-1]
            print(f"[+] Yeni abonelik linki bulundu: {latest_subscription_url}")
            
            # 2. AŞAMA: O linkin içine gir ve gerçek sunucu listesini çek
            req_sub = urllib.request.Request(latest_subscription_url, headers=headers)
            with urllib.request.urlopen(req_sub, timeout=20) as sub_res:
                content = sub_res.read()
                
                # Base64 ile şifrelenmiş sunucu listesini çöz
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                except:
                    decoded = content.decode('utf-8')
                
                # Sadece '://' içeren gerçek sunucu linklerini al (Çöpleri at)
                server_links = [line for line in decoded.splitlines() if '://' in line]
                
                # 3. AŞAMA: Dosyayı SIFIRLA ve yeni sunucuları YAZ
                with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(server_links))
                
                print(f"[+] {len(server_links)} adet taze sunucu linki dosyaya yazıldı!")

    except Exception as e:
        print(f"[-] HATA: {e}")

if __name__ == "__main__":
    main()
