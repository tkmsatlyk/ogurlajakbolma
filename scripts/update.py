import os
import re
import requests

# Public Telegram kanalları
CHANNELS = [
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
]

# Çıktı dosyası
OUTPUT_FILE = "output/found_happ.txt"

# Telegram web sayfası için User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    )
}

# Sadece happ://crypt5 bağlantılarını yakala
CRYPT5_PATTERN = re.compile(
    r"happ://crypt5/[^\s<>'\"`]+",
    re.IGNORECASE,
)


def clean_link(link):
    """
    Telegram HTML'inden gelen bağlantının sonundaki
    gereksiz karakterleri temizler.
    """
    return link.rstrip(".,;:!?)]}>")


def get_channel_links(channel_url):
    """
    Public Telegram kanalının web sayfasını indirir
    ve happ://crypt5/... bağlantılarını bulur.
    """

    print(f"\nKanal taranıyor: {channel_url}")

    try:
        response = requests.get(
            channel_url,
            headers=HEADERS,
            timeout=30,
        )

        print(f"HTTP durum kodu: {response.status_code}")

        if response.status_code != 200:
            print(
                f"Kanal alınamadı: HTTP {response.status_code}"
            )
            return []

        links = CRYPT5_PATTERN.findall(response.text)

        cleaned = []

        for link in links:
            link = clean_link(link)

            if link not in cleaned:
                cleaned.append(link)

        print(f"Bulunan crypt5: {len(cleaned)}")

        return cleaned

    except requests.RequestException as error:
        print(f"HTTP hatası: {error}")
        return []

    except Exception as error:
        print(f"Beklenmeyen hata: {error}")
        return []


def main():

    # output klasörünü oluştur
    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True,
    )

    all_links = []
    seen = set()

    # Bütün kanalları sırayla tara
    for channel in CHANNELS:

        links = get_channel_links(channel)

        for link in links:

            if link not in seen:
                seen.add(link)
                all_links.append(link)

    # Dosyaya yaz
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        for link in all_links:
            file.write(link)
            file.write("\n")

    print("\n==============================")
    print("İŞLEM TAMAMLANDI")
    print("==============================")
    print(f"Toplam benzersiz crypt5: {len(all_links)}")
    print(f"Çıktı: {OUTPUT_FILE}")
    print("==============================")


if __name__ == "__main__":
    main()
