import urllib.request

HEADER = """#profile-title: 《_🜲 VØRÐR 🔱 ELITE-MAX 🔱_》
#profile-update-interval: 0
#support-url: 
#profile-web-page-url: 
#announce: 《_🜲 VØRÐR 🔱_》⚠️ Ham Veri Canavari 🚨
#subscription-userinfo: upload=0; download=0; total=0; expire=0
"""

# Sadece bu "Pro" kaynaklar yeter
PRO_SOURCES = [
    "https://raw.githubusercontent.com/ShadowException/VPN/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/v2ray/v2ray.txt"
]

def main():
    final_content = HEADER
    
    for url in PRO_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                # BU SEFER RE.FINDALL YOK! Dosyayı olduğu gibi ham çekiyoruz.
                raw_data = response.read().decode('utf-8', errors='ignore')
                final_content += raw_data + "\n"
        except: continue

    # Dosyayı yaz
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
        f.write(final_content)

if __name__ == "__main__":
    main()
