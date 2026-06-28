import urllib.request
import re

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱 ELITE-MAX 🔱_》
#profile-update-interval: 0
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Sadece %100 Pro & Hızlı Linkler 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# Sadece "Kalite Garantili" 3 Dev Kaynak
PRO_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/v2ray/v2ray.txt"
]

# Bayrak eşleştirme sözlüğü (Sadece en pro ülkeler)
FLAGS = {
    "Germany": "🇩🇪", "Japan": "🇯🇵", "Netherlands": "🇳🇱", 
    "USA": "🇺🇸", "Singapore": "🇸🇬", "Canada": "🇨🇦", 
    "Hong Kong": "🇭🇰", "South Korea": "🇰🇷", "France": "🇫🇷"
}

def main():
    print("[+] VØRÐR Cerrahi Elemeye Başladı...")
    collected_links = set()
    
    for url in PRO_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                # Sadece en güçlü protokolleri al: Reality, Hysteria, VLESS
                links = re.findall(r'(vless|vmess|trojan|hysteria|tuic)://[^\s"\'<>]+', content, re.IGNORECASE)
                for link in links:
                    # Google, Yandex gibi "sahte" veya "çöp" olanları engelle
                    if "google" not in link.lower() and "yandex" not in link.lower():
                        collected_links.add(link)
        except:
            continue

    # Sadece en iyi 500 linki alıyoruz ki test yaparken telefonun yanmasın!
    final_list = list(collected_links)[:500] 

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for i, link in enumerate(final_list, 1):
            # Bayrak ve İsimlendirme
            country_name = "Global"
            flag = "🌐"
            for country in FLAGS:
                if country.lower() in link.lower():
                    country_name = country
                    flag = FLAGS[country]
            
            # İsmi tertemiz yap: 001. 🇩🇪 Germany | VORDR PRO
            name = f"{i:03d}. {flag} {country_name} | VORDR PRO"
            
            if "#" in link:
                clean_link = link.split("#")[0] + f"#{name}"
            else:
                clean_link = link + f"#{name}"
                
            f.write(clean_link + "\n")

    print(f"[+] {len(final_list)} adet 'Cerrah Onaylı' Pro link yüklendi!")

if __name__ == "__main__":
    main()
