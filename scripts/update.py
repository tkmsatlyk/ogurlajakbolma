import os
import re
import subprocess
import requests

# =========================
# AYARLAR
# =========================

CHANNELS = [
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
]

OUTPUT_FILE = "output_happ.txt"
DECRYPTED_FILE = "decrypted_links.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    )
}

# happ://crypt5/.... şeklindeki bağlantıları bul
CRYPT5_PATTERN = re.compile(
    r"happ://crypt5/[A-Za-z0-9_\-+/=]+",
    re.IGNORECASE
)


# =========================
# LINK TEMİZLE
# =========================

def clean_link(link):
    """
    Telegram HTML'sinden gelen bağlantının
    sonundaki gereksiz karakterleri temizler.
    """

    link = link.strip()

    link = link.rstrip(
        '.,;:!?)]}>\'"'
    )

    return link


# =========================
# TELEGRAM KANALI TARA
# =========================

def get_channel_links(channel_url):

    print()
    print("=" * 50)
    print(f"Kanal taranıyor: {channel_url}")
    print("=" * 50)

    try:
        response = requests.get(
            channel_url,
            headers=HEADERS,
            timeout=30
        )

        print(f"HTTP durum kodu: {response.status_code}")

        if response.status_code != 200:
            print("Kanal alınamadı.")
            return []

        links = CRYPT5_PATTERN.findall(response.text)

        cleaned = []

        for link in links:

            link = clean_link(link)

            if link not in cleaned:
                cleaned.append(link)

        print(f"Bulunan crypt5: {len(cleaned)}")

        for link in cleaned:
            print(link)

        return cleaned

    except requests.RequestException as error:
        print(f"HTTP hatası: {error}")
        return []

    except Exception as error:
        print(f"Beklenmeyen hata: {error}")
        return []


# =========================
# HPWNR BUL
# =========================

def find_hpwnr():

    possible_names = [
        "hpwnr",
        "./hpwnr",
        "hpwnr.exe",
        "./hpwnr.exe",
    ]

    for name in possible_names:

        if os.path.isfile(name):
            return name

    return None


# =========================
# CRYPT5 ÇÖZ
# =========================

def decrypt_crypt5(link):

    """
    hpwnr mevcutsa crypt5 bağlantısını çözer.

    Örnek:
        hpwnr happ://crypt5/...
    """

    hpwnr = find_hpwnr()

    if not hpwnr:
        return None

    try:

        result = subprocess.run(
            [hpwnr, link],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:

            print(
                "Decrypt hata:",
                result.stderr.strip()
            )

            return None

        output = result.stdout.strip()

        # hpwnr çıktısından URL bul
        match = re.search(
            r"https?://[^\s]+",
            output
        )

        if match:
            return match.group(0)

        return output

    except subprocess.TimeoutExpired:

        print("Decrypt zaman aşımına uğradı.")
        return None

    except Exception as error:

        print(
            f"Decrypt çalıştırma hatası: {error}"
        )

        return None


# =========================
# ANA PROGRAM
# =========================

def main():

    all_links = []
    seen = set()

    # -------------------------
    # Telegram kanallarını tara
    # -------------------------

    for channel in CHANNELS:

        links = get_channel_links(channel)

        for link in links:

            if link not in seen:

                seen.add(link)
                all_links.append(link)

    # -------------------------
    # Hiç link yoksa
    # -------------------------

    if not all_links:

        print()
        print("Hiç crypt5 bulunamadı.")
        return

    # -------------------------
    # Crypt5'leri kaydet
    # -------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for link in all_links:

            file.write(link)
            file.write("\n")

    print()
    print("=" * 50)
    print("CRYPT5 TOPLAMA TAMAMLANDI")
    print("=" * 50)

    print(
        f"Toplam crypt5: {len(all_links)}"
    )

    print(
        f"Dosya: {OUTPUT_FILE}"
    )

    # -------------------------
    # hpwnr var mı?
    # -------------------------

    hpwnr = find_hpwnr()

    if not hpwnr:

        print()
        print(
            "hpwnr bulunamadı."
        )
        print(
            "Bu nedenle sadece crypt5 bağlantıları "
            "kaydedildi."
        )

        return

    # -------------------------
    # Çözülmüş sonuçları al
    # -------------------------

    decrypted = []

    print()
    print("=" * 50)
    print("CRYPT5 ÇÖZÜLÜYOR")
    print("=" * 50)

    for index, link in enumerate(
        all_links,
        start=1
    ):

        print(
            f"[{index}/{len(all_links)}] Çözülüyor..."
        )

        result = decrypt_crypt5(link)

        if result:

            print(
                f"Sonuç: {result}"
            )

            decrypted.append(result)

        else:

            print(
                "Çözülemedi."
            )

    # -------------------------
    # Sonuçları kaydet
    # -------------------------

    with open(
        DECRYPTED_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for link in decrypted:

            file.write(link)
            file.write("\n")

    print()
    print("=" * 50)
    print("İŞLEM TAMAMLANDI")
    print("=" * 50)

    print(
        f"Bulunan crypt5 : {len(all_links)}"
    )

    print(
        f"Çözülen        : {len(decrypted)}"
    )

    print(
        f"Crypt5 dosyası : {OUTPUT_FILE}"
    )

    print(
        f"Sonuç dosyası  : {DECRYPTED_FILE}"
    )


if __name__ == "__main__":
    main()
