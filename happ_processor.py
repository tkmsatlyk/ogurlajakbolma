import os
import re
import subprocess
import requests
from bs4 import BeautifulSoup


# ============================================================
# AYARLAR
# ============================================================

CHANNELS = [
    "https://t.me/s/happvpn",
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
]

OUTPUT_FILE = "toplanan_linkler.txt"

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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Telegram mesajından happ://crypt5 bağlantısını yakalar
CRYPT5_PATTERN = re.compile(
    r"happ://crypt5/[^\s<>'\"]+",
    re.IGNORECASE,
)

# Desteklediğimiz VPN/proxy URI'leri
VPN_PATTERN = re.compile(
    r"(?:"
    r"vless://[^\s<>'\"]+|"
    r"vmess://[^\s<>'\"]+|"
    r"trojan://[^\s<>'\"]+|"
    r"ss://[^\s<>'\"]+|"
    r"ssr://[^\s<>'\"]+|"
    r"tuic://[^\s<>'\"]+|"
    r"hysteria://[^\s<>'\"]+|"
    r"hysteria2://[^\s<>'\"]+|"
    r"socks5://[^\s<>'\"]+"
    r")",
    re.IGNORECASE,
)


# ============================================================
# HPWNR ÇALIŞTIR
# ============================================================

def hpwnr(*args):
    """
    hpwnr programını çalıştırır.

    Örnek:
        hpwnr("happ://crypt5/....")

    veya:
        hpwnr("https://site.com/sub", "uri")
    """

    try:
        result = subprocess.run(
            ["hpwnr", *args],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            error = result.stderr.strip()

            print("hpwnr HATASI:")
            print(error)

            return ""

        return result.stdout.strip()

    except FileNotFoundError:
        print("HATA: hpwnr bulunamadı!")
        print("GitHub Actions içinde hpwnr kurulum adımını kontrol et.")
        return ""

    except subprocess.TimeoutExpired:
        print("HATA: hpwnr zaman aşımına uğradı.")
        return ""

    except Exception as e:
        print(f"hpwnr çalıştırma hatası: {e}")
        return ""


# ============================================================
# TELEGRAM'DAN CRYPT5 ÇEK
# ============================================================

def get_crypt5_links(channel_url):
    print()
    print("=" * 60)
    print(f"Telegram kanalı taranıyor: {channel_url}")
    print("=" * 60)

    try:
        response = requests.get(
            channel_url,
            headers=HEADERS,
            timeout=30,
        )

        print(f"HTTP durum kodu: {response.status_code}")

        if response.status_code != 200:
            print("Kanal alınamadı.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        messages = soup.find_all(
            "div",
            class_="tgme_widget_message_text",
        )

        found = []

        # Yeni mesajlardan eski mesajlara doğru
        for message in reversed(messages):

            text = message.get_text(" ", strip=True)

            links = CRYPT5_PATTERN.findall(text)

            for link in links:

                # Telegram HTML'den gelebilecek noktalama işaretlerini temizle
                link = link.rstrip(".,;:!?)]}\"'")

                if link not in found:
                    found.append(link)

        print(f"Bulunan crypt5 sayısı: {len(found)}")

        return found

    except requests.RequestException as e:
        print(f"Telegram HTTP hatası: {e}")
        return []

    except Exception as e:
        print(f"Telegram tarama hatası: {e}")
        return []


# ============================================================
# CRYPT5 ÇÖZ
# ============================================================

def decrypt_crypt5(crypt_link):
    print()
    print("-" * 60)
    print("CRYPT5 çözülüyor...")
    print(crypt_link[:100] + ("..." if len(crypt_link) > 100 else ""))

    # hpwnr gerçek crypt5 çözme işlemini yapıyor.
    # Argüman olarak sadece crypt5 linki veriyoruz.
    decrypted = hpwnr(crypt_link)

    if not decrypted:
        print("Crypt5 çözülemedi.")
        return ""

    print("Crypt5 çözme sonucu:")
    print(decrypted[:300])

    # Sonuç içerisinde HTTPS varsa onu yakala.
    https_match = re.search(
        r"https?://[^\s<>'\"]+",
        decrypted,
        re.IGNORECASE,
    )

    if https_match:
        url = https_match.group(0).rstrip(".,;:!?)]}\"'")

        print("HTTPS abonelik bulundu:")
        print(url)

        return url

    # Bazı durumlarda hpwnr doğrudan URL döndürebilir.
    if decrypted.startswith(("http://", "https://")):
        return decrypted.strip()

    print("Çözüm sonucunda HTTPS adresi bulunamadı.")

    return ""


# ============================================================
# HTTPS ABONELİĞİNDEN VPN LİNKLERİNİ AL
# ============================================================

def get_vpn_links(subscription_url):
    print()
    print("-" * 60)
    print("Abonelik işleniyor:")
    print(subscription_url)

    # hpwnr'ın fetch + URI conversion özelliğini kullanıyoruz.
    #
    # https://... uri
    #
    # Böylece abonelik içeriğini alıp VPN URI'lerine dönüştürüyor.
    converted = hpwnr(
        subscription_url,
        "uri",
    )

    if not converted:
        print("Abonelikten sonuç alınamadı.")

        # Fallback olarak requests ile direkt deneyelim.
        try:
            response = requests.get(
                subscription_url,
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code == 200:
                converted = response.text

        except Exception as e:
            print(f"Fallback HTTP hatası: {e}")

    if not converted:
        return []

    vpn_links = VPN_PATTERN.findall(converted)

    cleaned = []

    for link in vpn_links:

        link = link.strip()

        # Sonuna gelebilecek noktalama işaretlerini temizle
        link = link.rstrip(".,;:!?)]}\"'")

        if link not in cleaned:
            cleaned.append(link)

    print(f"Bulunan VPN linki: {len(cleaned)}")

    return cleaned


# ============================================================
# İSİM EKLE
# ============================================================

def add_names(links):
    result = []

    for index, link in enumerate(links):

        name = NAMES[index % len(NAMES)]

        # Eski fragment'ı temizle
        base_link = link.split("#", 1)[0]

        result.append(
            f"{base_link}#{name}"
        )

    return result


# ============================================================
# ANA İŞLEM
# ============================================================

def update_toplanan_linkler():

    all_vpn_links = []
    seen = set()

    # --------------------------------------------------------
    # 1. TÜM TELEGRAM KANALLARINI TARA
    # --------------------------------------------------------

    for channel in CHANNELS:

        crypt5_links = get_crypt5_links(channel)

        for crypt_link in crypt5_links:

            # ------------------------------------------------
            # 2. CRYPT5 ÇÖZ
            # ------------------------------------------------

            subscription_url = decrypt_crypt5(crypt_link)

            if not subscription_url:
                continue

            # ------------------------------------------------
            # 3. HTTPS ABONELİĞİNDEN VPN LİNKLERİNİ AL
            # ------------------------------------------------

            vpn_links = get_vpn_links(subscription_url)

            # ------------------------------------------------
            # 4. DUPLICATE TEMİZLE
            # ------------------------------------------------

            for link in vpn_links:

                clean_link = link.split("#", 1)[0]

                if clean_link not in seen:

                    seen.add(clean_link)
                    all_vpn_links.append(clean_link)

    # --------------------------------------------------------
    # 5. İLK 10 VPN
    # --------------------------------------------------------

    top_10 = all_vpn_links[:10]

    print()
    print("=" * 60)
    print(f"Toplam benzersiz VPN: {len(all_vpn_links)}")
    print(f"Dosyaya yazılacak VPN: {len(top_10)}")
    print("=" * 60)

    if not top_10:

        print()
        print("HİÇ VPN LİNKİ BULUNAMADI!")
        print()
        return False

    # --------------------------------------------------------
    # 6. İSİMLERİ SIRAYLA EKLE
    # --------------------------------------------------------

    final_links = add_names(top_10)

    # --------------------------------------------------------
    # 7. ESKİ DOSYAYI TAMAMEN SİLİP YENİSİNİ YAZ
    # --------------------------------------------------------

    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            for link in final_links:

                file.write(link)
                file.write("\n")

        print()
        print("=" * 60)
        print("BAŞARILI!")
        print("=" * 60)
        print(f"Güncel dosya: {OUTPUT_FILE}")
        print()

        for index, link in enumerate(final_links, start=1):

            print(f"{index}. {link}")

        print()
        print("Eski içerik temizlendi.")
        print("Yeni VPN linkleri dosyaya yazıldı.")

        return True

    except Exception as e:

        print(f"Dosya yazma hatası: {e}")

        return False


# ============================================================
# PROGRAM
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================================")
    print(" HAPP CRYPT5 VPN GÜNCELLEYİCİ")
    print("==============================================")
    print()

    success = update_toplanan_linkler()

    if success:
        print()
        print("TÜM İŞLEMLER TAMAMLANDI.")
    else:
        print()
        print("İŞLEM BAŞARISIZ.")
