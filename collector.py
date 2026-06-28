import urllib.request
import re

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱 ELITE-MAX 🔱_》
#profile-update-interval: 0
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Sadece %100 Pro & Hızlı Linkler 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

PRO_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/v2ray/v2ray.txt"
]

FLAGS = {
    "Germany": "🇩🇪", "Japan": "🇯🇵", "Netherlands": "🇳🇱", 
    "USA": "🇺🇸", "Singapore": "🇸🇬", "Canada": "🇨🇦", 
    "Hong Kong": "🇭🇰", "South Korea": "🇰🇷", "France": "🇫🇷"
}

def main():
    collected_links = []
    
    for url in PRO_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                # Bu sefer linklerin tamamını yakalıyoruz
                links = re.findall(r'(vless|vmess|trojan|hysteria|tuic)://[^\s#]+', content, re.IGNORECASE)
                for link in links:
                    if "google" not in link.lower() and "yandex" not in link.lower():
                        collected_links.append(link)
        except: continue

    # Tekrar edenleri sil
    unique_links = list(set(collected_links))[:500]

    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(HEADER)
        for i, link in enumerate(unique_links, 1):
            country_name = "Global"
            flag = "🌐"
            for country in FLAGS:
                if country.lower() in link.lower():
                    country_name = country
                    flag = FLAGS[country]
            
            # Linkin kendisini bozmadan sadece sonuna isim ekliyoruz
            final_link = f"{link}#{i:03d}. {flag} {country_name} | VORDR PRO"
            f.write(final_link + "\n")

if __name__ == "__main__":
    main()
