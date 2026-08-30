import base64
import html
import os
import re
import subprocess
import urllib.request
import urllib.error


# ============================================================
# AYARLAR
# ============================================================

CHANNELS = [
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
]

OUTPUT_FILE = "Toplanan_linkler.txt"

NAMES = [
    "🇺🇸 UNITED STATES",
    "🇯🇵 JAPAN",
    "🇰🇷 SOUTH KOREA",
    "🇦🇪 UNITED ARAB EMIRATES",
    "🇨🇭 SWITZERLAND",
    "🇸🇬 SINGAPORE",
    "🇮🇸 ICELAND",
    "🇨🇦 CANADA",
    "🇳🇴 NORWAY",
    "🇸🇪 SWEDEN",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    )
}


# ============================================================
# LINK PATTERNLERİ
# ============================================================

HAPP_PATTERN = re.compile(
    r'happ://(?:crypt|crypt2|crypt3|crypt4|crypt5)/[^\s<>"\']+',
    re.IGNORECASE,
)

VPN_PATTERN = re.compile(
    r'(?:'
    r'vless://[^\s<>"\']+'
    r'|vmess://[^\s<>"\']+'
    r'|trojan://[^\s<>"\']+'
    r'|ss://[^\s<>"\']+'
    r'|ssr://[^\s<>"\']+'
    r'|tuic://[^\s<>"\']+'
    r'|hysteria2://[^\s<>"\']+'
    r'|hy2://[^\s<>"\']+'
    r'|socks5://[^\s<>"\']+'
    r')',
    re.IGNORECASE,
)


# ============================================================
# GENEL YARDIMCI FONKSİYONLAR
# ============================================================

def clean_link(link):
    """HTML'den gelen linkin gereksiz karakterlerini temizler."""

    link = html.unescape(link)

    link = link.strip()

    # Telegram HTML'sinden gelebilecek son karakterler
    link = link.rstrip('.,;:!?)]}\'"<>')

    return link


def http_get(url):
    """requests kullanmadan HTTP GET."""

    request = urllib.request.Request(
        url,
        headers=HEADERS,
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()

        charset = response.headers.get_content_charset() or "utf-8"

        return data.decode(charset, errors="ignore")


# ============================================================
# TELEGRAM KANALINI TARA
# ============================================================

def get_channel_happ_links(channel_url):

    print()
    print("=" * 60)
    print(f"KANAL TARANIYOR: {channel_url}")
    print("=" * 60)

    try:

        content = http_get(channel_url)

        links = HAPP_PATTERN.findall(content)

        cleaned = []

        for link in links:

            link = clean_link(link)

            if link not in cleaned:
                cleaned.append(link)

        print(f"Bulunan HAPP linkleri: {len(cleaned)}")

        for link in cleaned:
            print(f"  {link}")

        return cleaned

    except Exception as error:

        print(f"Telegram kanalı okunamadı: {error}")

        return []


# ============================================================
# HAPP / CRYPT5 ÇÖZ
# ============================================================

def decrypt_happ(happ_link):

    print()
    print("-" * 60)
    print("HAPP ÇÖZÜLÜYOR")
    print("-" * 60)

    print(happ_link)

    try:

        result = subprocess.run(
            ["hpwnr", happ_link],
            capture_output=True,
            text=True,
            timeout=60,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:

            print("HAPP çözülemedi.")

            if stderr:
                print("Hata:")
                print(stderr)

            return None

        if not stdout:

            print("hpwnr boş sonuç döndürdü.")

            return None

        print("hpwnr sonucu:")
        print(stdout)

        # Sonuç içinde https/http ara
        url_match = re.search(
            r'https?://[^\s<>"\']+',
            stdout,
            re.IGNORECASE,
        )

        if url_match:

            resolved = clean_link(url_match.group(0))

            print()
            print("ÇÖZÜLEN HTTPS:")
            print(resolved)

            return resolved

        # Bazı durumlarda çıktı doğrudan URL olabilir
        if stdout.startswith(("http://", "https://")):

            return clean_link(stdout)

        print("Çözüm sonucunda HTTPS bulunamadı.")

        return None

    except FileNotFoundError:

        print()
        print("HATA: hpwnr bulunamadı!")
        print("GitHub Actions içinde hpwnr kurulum adımını kontrol et.")

        return None

    except subprocess.TimeoutExpired:

        print("hpwnr zaman aşımına uğradı.")

        return None

    except Exception as error:

        print(f"HAPP çözme hatası: {error}")

        return None


# ============================================================
# BASE64 KONTROLÜ
# ============================================================

def try_base64_decode(text):

    text = text.strip()

    if not text:
        return text

    try:

        # URL-safe base64 de destekle
        decoded = base64.b64decode(
            text + "=" * (-len(text) % 4),
            validate=False,
        )

        decoded_text = decoded.decode(
            "utf-8",
            errors="ignore",
        )

        # Gerçekten anlamlı bir sonuçsa kullan
        if "://" in decoded_text:

            return decoded_text

    except Exception:
        pass

    return text


# ============================================================
# HTTPS ABONELİĞİNİ AÇ
# ============================================================

def get_subscription(url):

    print()
    print("-" * 60)
    print("HTTPS ABONELİĞİ AÇILIYOR")
    print("-" * 60)

    print(url)

    try:

        content = http_get(url)

        print(f"İndirilen veri: {len(content)} karakter")

        # Önce normal içerikte link ara
        links = VPN_PATTERN.findall(content)

        if links:

            print(f"Doğrudan bulunan VPN linki: {len(links)}")

            return links

        # Base64 ise çözmeyi dene
        decoded = try_base64_decode(content)

        if decoded != content:

            links = VPN_PATTERN.findall(decoded)

            if links:

                print(
                    f"Base64 çözüldükten sonra bulunan VPN linki: "
                    f"{len(links)}"
                )

                return links

        print("Bu HTTPS içinde VPN linki bulunamadı.")

        return []

    except urllib.error.HTTPError as error:

        print(f"HTTP hatası: {error.code}")

        return []

    except urllib.error.URLError as error:

        print(f"Bağlantı hatası: {error}")

        return []

    except Exception as error:

        print(f"Abonelik okuma hatası: {error}")

        return []


# ============================================================
# TEK LİNKİ İŞLE
# ============================================================

def process_happ_link(happ_link):

    resolved_url = decrypt_happ(happ_link)

    if not resolved_url:
        return []

    if not resolved_url.startswith(
        ("http://", "https://")
    ):
        print("Çözülmüş değer HTTPS değil.")

        return []

    vpn_links = get_subscription(resolved_url)

    return vpn_links


# ============================================================
# ANA İŞLEM
# ============================================================

def main():

    print()
    print("=" * 60)
    print("HAPP -> CRYPT5 -> HTTPS -> VPN TOPLAYICI")
    print("=" * 60)

    all_happ_links = []
    all_vpn_links = []

    # --------------------------------------------------------
    # 1. Telegram kanallarından HAPP linklerini al
    # --------------------------------------------------------

    for channel in CHANNELS:

        links = get_channel_happ_links(channel)

        for link in links:

            if link not in all_happ_links:
                all_happ_links.append(link)

    print()
    print("=" * 60)
    print(f"TOPLAM HAPP LINKİ: {len(all_happ_links)}")
    print("=" * 60)

    # --------------------------------------------------------
    # 2. HAPP linklerini çöz
    # 3. İçindeki HTTPS adresine gir
    # 4. VPN linklerini al
    # --------------------------------------------------------

    for index, happ_link in enumerate(
        all_happ_links,
        start=1,
    ):

        print()
        print(
            f"[{index}/{len(all_happ_links)}] "
            "İŞLENİYOR"
        )

        vpn_links = process_happ_link(happ_link)

        for link in vpn_links:

            link = clean_link(link)

            if link not in all_vpn_links:

                all_vpn_links.append(link)

    # --------------------------------------------------------
    # 5. İsimleri sırayla ver
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(f"TOPLAM VPN LINKİ: {len(all_vpn_links)}")
    print("=" * 60)

    if not all_vpn_links:

        print()
        print("HİÇ VPN LINKİ BULUNAMADI.")
        print()
        return

    processed_links = []

    for index, link in enumerate(all_vpn_links):

        name = NAMES[index % len(NAMES)]

        # Eski #etiket varsa kaldır
        link = link.split("#", 1)[0]

        final_link = f"{link}#{name}"

        processed_links.append(final_link)

    # --------------------------------------------------------
    # 6. Dosyaya yaz
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        for link in processed_links:

            file.write(link)
            file.write("\n")

    # --------------------------------------------------------
    # 7. Sonuç
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("İŞLEM TAMAMLANDI")
    print("=" * 60)

    print(
        f"Toplam VPN linki: {len(processed_links)}"
    )

    print(
        f"Çıktı dosyası: {OUTPUT_FILE}"
    )

    print("=" * 60)


# ============================================================
# ÇALIŞTIR
# ============================================================

if __name__ == "__main__":
    main()
