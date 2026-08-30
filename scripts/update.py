import os
import re
import base64
import subprocess
import tempfile
import requests


# =========================================================
# AYARLAR
# =========================================================

CHANNELS = [
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
]

OUTPUT_FILE = "Toplanan_linkler.txt"


# Linklere sırayla verilecek isimler
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
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    )
}


CRYPT5_PATTERN = re.compile(
    r"happ://crypt5/[A-Za-z0-9_\-+/=]+",
    re.IGNORECASE
)


VPN_PATTERN = re.compile(
    r"(?:"
    r"vless://[^\s<>'\"]+|"
    r"vmess://[^\s<>'\"]+|"
    r"trojan://[^\s<>'\"]+|"
    r"ss://[^\s<>'\"]+|"
    r"ssr://[^\s<>'\"]+|"
    r"tuic://[^\s<>'\"]+|"
    r"hysteria2://[^\s<>'\"]+|"
    r"hy2://[^\s<>'\"]+"
    r")",
    re.IGNORECASE
)


# =========================================================
# HPWNR
# =========================================================

def hpwnr_command(*args, cwd=None):

    try:

        result = subprocess.run(
            ["hpwnr", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:

            print("hpwnr hata:")
            print(result.stderr.strip())

            return None

        return result.stdout.strip()

    except FileNotFoundError:

        print("HATA: hpwnr bulunamadı.")

        return None

    except subprocess.TimeoutExpired:

        print("hpwnr zaman aşımına uğradı.")

        return None

    except Exception as e:

        print(f"hpwnr çalıştırma hatası: {e}")

        return None


# =========================================================
# TELEGRAM'DAN CRYPT5 TOPLA
# =========================================================

def get_crypt5_links(channel_url):

    print()
    print("=" * 60)
    print("KANAL:", channel_url)
    print("=" * 60)

    try:

        response = requests.get(
            channel_url,
            headers=HEADERS,
            timeout=30
        )

        print("HTTP:", response.status_code)

        if response.status_code != 200:
            return []

        found = CRYPT5_PATTERN.findall(
            response.text
        )

        result = []

        for link in found:

            link = link.rstrip(
                ".,;:!?)]}>'\""
            )

            if link not in result:
                result.append(link)

        print(
            f"Bulunan crypt5: {len(result)}"
        )

        return result

    except Exception as e:

        print(
            f"Telegram kanal hatası: {e}"
        )

        return []


# =========================================================
# CRYPT5 ÇÖZ
# =========================================================

def decrypt_crypt5(crypt5):

    print()
    print("Crypt5 çözülüyor:")
    print(crypt5)

    result = hpwnr_command(
        crypt5
    )

    if not result:
        return None

    # hpwnr çıktısından HTTPS bul
    match = re.search(
        r"https?://[^\s<>'\"]+",
        result
    )

    if not match:

        print(
            "HTTPS adresi bulunamadı."
        )

        return None

    url = match.group(0).rstrip(
        ".,;:!?)]}>'\""
    )

    print(
        "Çözülen URL:",
        url
    )

    return url


# =========================================================
# ABONELİĞİ HPWNR İLE ÇEK
# =========================================================

def fetch_subscription(url):

    """
    hpwnr ile aboneliği indirir.

    Happ aboneliklerinde gerekli response
    şifrelemesi varsa hpwnr bunu da çözebilir.
    """

    print()
    print("Abonelik indiriliyor:")
    print(url)

    with tempfile.TemporaryDirectory() as temp_dir:

        result = hpwnr_command(
            url,
            "fetch",
            "ua",
            "happ",
            cwd=temp_dir
        )

        # Küçük cevap stdout'ta olabilir
        content = result or ""

        # Büyük cevaplarda hpwnr dosya oluşturabilir
        try:

            files = os.listdir(temp_dir)

            for filename in files:

                if filename.startswith(
                    "hpwnresp_"
                ):

                    filepath = os.path.join(
                        temp_dir,
                        filename
                    )

                    with open(
                        filepath,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:

                        content = f.read()

                    break

        except Exception:
            pass

        if not content:
            print(
                "Abonelik içeriği boş."
            )
            return ""

        # Base64 abonelikse çözmeyi dene
        stripped = content.strip()

        try:

            decoded = base64.b64decode(
                stripped,
                validate=True
            )

            decoded_text = decoded.decode(
                "utf-8",
                errors="ignore"
            )

            # Gerçekten okunabilir bir içerikse kullan
            if "://" in decoded_text:

                content = decoded_text

        except Exception:
            pass

        print(
            "Abonelik alındı."
        )

        return content


# =========================================================
# VPN LINKLERİNİ ÇIKAR
# =========================================================

def extract_vpn_links(content):

    links = VPN_PATTERN.findall(
        content
    )

    result = []

    for link in links:

        link = link.strip().rstrip(
            ".,;:!?)]}>'\""
        )

        # Mevcut # ismini kaldır
        link = link.split("#", 1)[0]

        if link not in result:

            result.append(link)

    return result


# =========================================================
# ANA PROGRAM
# =========================================================

def main():

    all_crypt5 = []
    seen_crypt5 = set()

    # -----------------------------------------------------
    # 1. Telegram kanallarını tara
    # -----------------------------------------------------

    for channel in CHANNELS:

        links = get_crypt5_links(
            channel
        )

        for link in links:

            if link not in seen_crypt5:

                seen_crypt5.add(link)
                all_crypt5.append(link)

    print()
    print(
        "TOPLAM CRYPT5:",
        len(all_crypt5)
    )

    if not all_crypt5:

        print(
            "Hiç crypt5 bulunamadı."
        )

        return

    # -----------------------------------------------------
    # 2. Crypt5 -> HTTPS
    # -----------------------------------------------------

    subscription_urls = []
    seen_urls = set()

    for crypt5 in all_crypt5:

        url = decrypt_crypt5(
            crypt5
        )

        if url and url not in seen_urls:

            seen_urls.add(url)
            subscription_urls.append(url)

    print()
    print(
        "ÇÖZÜLEN HTTPS:",
        len(subscription_urls)
    )

    # -----------------------------------------------------
    # 3. HTTPS aboneliklerine gir
    # -----------------------------------------------------

    all_vpn_links = []
    seen_vpn = set()

    for url in subscription_urls:

        content = fetch_subscription(
            url
        )

        if not content:
            continue

        vpn_links = extract_vpn_links(
            content
        )

        print(
            "Bulunan VPN:",
            len(vpn_links)
        )

        for link in vpn_links:

            if link not in seen_vpn:

                seen_vpn.add(link)
                all_vpn_links.append(link)

    # -----------------------------------------------------
    # 4. İsimleri sırayla ekle
    # -----------------------------------------------------

    final_links = []

    for index, link in enumerate(
        all_vpn_links
    ):

        name = NAMES[
            index % len(NAMES)
        ]

        final_links.append(
            f"{link}#{name}"
        )

    # -----------------------------------------------------
    # 5. Dosyaya yaz
    # -----------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for link in final_links:

            file.write(link)
            file.write("\n")

    # -----------------------------------------------------
    # SONUÇ
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("İŞLEM TAMAMLANDI")
    print("=" * 60)

    print(
        "Crypt5:",
        len(all_crypt5)
    )

    print(
        "HTTPS:",
        len(subscription_urls)
    )

    print(
        "VPN:",
        len(final_links)
    )

    print(
        "Dosya:",
        OUTPUT_FILE
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
