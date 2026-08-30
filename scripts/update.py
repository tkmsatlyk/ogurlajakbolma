import re
import requests

CHANNELS = [
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
]

OUTPUT_FILE = "output/found_happ.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

PATTERN = re.compile(r"happ://crypt5/[^\s<>'\"`]+")


def main():
    found = []
    seen = set()

    for channel in CHANNELS:
        print(f"Taranıyor: {channel}")

        response = requests.get(
            channel,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        links = PATTERN.findall(response.text)

        for link in links:
            if link not in seen:
                seen.add(link)
                found.append(link)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for link in found:
            file.write(link + "\n")

    print(f"Bulunan crypt5 linki: {len(found)}")
    print(f"Kaydedildi: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
