import urllib.request

# Ares'in "i" harfine basınca çıkan o gerçek abonelik linkini buraya yapıştır!
# Örnek: https://aresvpn-linki.com/....
SUBSCRIPTION_URL = "BURAYA_GERCEK_ABONELIK_LINKINI_YAPISTIR"

def main():
    try:
        # Abonelik linkini bir tarayıcı gibi ziyaret et
        req = urllib.request.Request(SUBSCRIPTION_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            # Tüm sunucu listesini (VLESS, Shadowsocks vb.) olduğu gibi al
            server_list = response.read().decode('utf-8')
            
            # İçeriği dosyaya tertemiz yaz
            with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
                f.write(server_list)
                
            print("[+] Tüm sunucu listesi başarıyla çekildi ve güncellendi!")
                
    except Exception as e:
        print(f"[-] Hata oluştu: {e}")

if __name__ == "__main__":
    main()
