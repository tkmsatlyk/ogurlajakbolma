import base64
import html
import re
import subprocess
import urllib.request
import urllib.error
from html.parser import HTMLParser
from datetime import datetime

# ============================================================
# AYARLAR
# ============================================================

CHANNELS = [
    "https://t.me/s/happvpn",
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
    "https://t.me/s/expensive_vpn",
]

OUTPUT_FILE = "Toplanan_linkler.txt"


# ============================================================
# names.txt DOSYASINDAN İSİMLERİ OKU
# ============================================================

def load_names():

    try:

        with open(
            "names.txt",
            "r",
            encoding="utf-8",
        ) as file:

            names = [
                line.strip()
                for line in file
                if line.strip()
            ]

        if not names:

            print()
            print(
                "UYARI: names.txt boş!"
            )

            return []

        print()
        print(
            f"names.txt içinden "
            f"{len(names)} isim yüklendi."
        )

        return names

    except FileNotFoundError:

        print()
        print(
            "HATA: names.txt bulunamadı!"
        )

        return []


NAMES = load_names()


# ============================================================
# SADECE CRYPT5
# ============================================================

CRYPT5_PATTERN = re.compile(
    r'happ://crypt5/[^\s<>"\']+',
    re.IGNORECASE,
)


# ============================================================
# VPN LINKLERİ
# ============================================================

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

    link = html.unescape(link)

    link = link.strip()

    link = link.rstrip(
        '.,;:!?)]}\'"<>'
    )

    return link


def http_get(url):

    request = urllib.request.Request(
        url,
        headers=HEADERS,
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:

        data = response.read()

        charset = (
            response.headers.get_content_charset()
            or "utf-8"
        )

        return data.decode(
            charset,
            errors="ignore",
        )


# ============================================================
# HTTP HEADERS
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    )
}


# ============================================================
# TELEGRAM MESAJ PARSER
# ============================================================

class TelegramMessageParser(HTMLParser):

    def __init__(self):

        super().__init__(
            convert_charrefs=True
        )

        self.message_depth = 0

        self.current_message = None

        self.messages = []

    def handle_starttag(
        self,
        tag,
        attrs,
    ):

        attrs_dict = dict(attrs)

        # Yeni Telegram mesajı
        if tag == "div":

            classes = attrs_dict.get(
                "class",
                "",
            )

            if (
                self.message_depth == 0
                and "tgme_widget_message"
                in classes.split()
            ):

                self.message_depth = 1

                self.current_message = {
                    "post": attrs_dict.get(
                        "data-post",
                        "",
                    ),
                    "datetime": None,
                    "links": [],
                }

                return

            # Mesajın içindeki div
            if self.message_depth > 0:

                self.message_depth += 1

        # Mesaj zamanı
        if (
            self.message_depth > 0
            and tag == "time"
        ):

            value = attrs_dict.get(
                "datetime"
            )

            if (
                value
                and self.current_message[
                    "datetime"
                ] is None
            ):

                self.current_message[
                    "datetime"
                ] = value

        # Attribute içinde crypt5 varsa
        if self.message_depth > 0:

            for value in attrs_dict.values():

                if not value:
                    continue

                for link in CRYPT5_PATTERN.findall(
                    value
                ):

                    link = clean_link(
                        link
                    )

                    if (
                        link
                        not in self.current_message[
                            "links"
                        ]
                    ):

                        self.current_message[
                            "links"
                        ].append(
                            link
                        )

    def handle_data(self, data):

        if self.message_depth <= 0:

            return

        for link in CRYPT5_PATTERN.findall(
            data
        ):

            link = clean_link(
                link
            )

            if (
                link
                not in self.current_message[
                    "links"
                ]
            ):

                self.current_message[
                    "links"
                ].append(
                    link
                )

    def handle_endtag(self, tag):

        if (
            self.message_depth <= 0
            or tag != "div"
        ):

            return

        self.message_depth -= 1

        if (
            self.message_depth == 0
            and self.current_message is not None
        ):

            self.messages.append(
                self.current_message
            )

            self.current_message = None


# ============================================================
# TÜM KANALLARDAKİ EN YENİ CRYPT5
# ============================================================

def get_latest_crypt5_from_all_channels():

    candidates = []

    for channel in CHANNELS:

        print()

        print("=" * 60)

        print(
            f"KANAL TARANIYOR: {channel}"
        )

        print("=" * 60)

        try:

            content = http_get(
                channel
            )

            parser = TelegramMessageParser()

            parser.feed(
                content
            )

            for message in parser.messages:

                if not message["links"]:

                    continue

                message_datetime = None

                if message["datetime"]:

                    try:

                        message_datetime = (
                            datetime.fromisoformat(
                                message[
                                    "datetime"
                                ].replace(
                                    "Z",
                                    "+00:00",
                                )
                            )
                        )

                    except ValueError:

                        message_datetime = None

                for link in message["links"]:

                    candidates.append(
                        {
                            "link": link,
                            "datetime": (
                                message_datetime
                            ),
                            "channel": channel,
                            "post": message[
                                "post"
                            ],
                        }
                    )

        except Exception as error:

            print(
                "Telegram kanalı okunamadı: "
                f"{error}"
            )

    # Hiç crypt5 yok
    if not candidates:

        print()

        print(
            "HİÇ happ://crypt5 LINKİ BULUNAMADI."
        )

        return None

    # Tarihi olanları kullan
    with_dates = [
        item
        for item in candidates
        if item["datetime"] is not None
    ]

    if with_dates:

        # Gerçekten en yeni mesaj
        latest = max(
            with_dates,
            key=lambda item: item[
                "datetime"
            ],
        )

    else:

        # Tarih okunamazsa son bulunanı kullan
        latest = candidates[-1]

    print()

    print("=" * 60)

    print(
        "SADECE EN YENİ CRYPT5 KULLANILACAK"
    )

    print("=" * 60)

    print(
        f"CRYPT5: {latest['link']}"
    )

    print(
        f"KAYNAK: {latest['channel']}"
    )

    if latest["datetime"]:

        print(
            f"ZAMAN: {latest['datetime']}"
        )

    if latest["post"]:

        print(
            f"MESAJ: {latest['post']}"
        )

    print("=" * 60)

    return latest["link"]


# ============================================================
# HAPP / CRYPT5 ÇÖZ
# ============================================================

def decrypt_happ(happ_link):

    print()

    print("-" * 60)

    print("HAPP ÇÖZÜLÜYOR")

    print("-" * 60)

    print(
        happ_link
    )

    try:

        result = subprocess.run(
            [
                "hpwnr",
                happ_link,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        stdout = result.stdout.strip()

        stderr = result.stderr.strip()

        if result.returncode != 0:

            print(
                "HAPP çözülemedi."
            )

            if stderr:

                print(
                    "Hata:"
                )

                print(
                    stderr
                )

            return None

        if not stdout:

            print(
                "hpwnr boş sonuç döndürdü."
            )

            return None

        print(
            "hpwnr sonucu:"
        )

        print(
            stdout
        )

        # HTTPS bul
        url_match = re.search(
            r'https?://[^\s<>"\']+',
            stdout,
            re.IGNORECASE,
        )

        if url_match:

            resolved = clean_link(
                url_match.group(0)
            )

            print()

            print(
                "ÇÖZÜLEN HTTPS:"
            )

            print(
                resolved
            )

            return resolved

        # Çıktı direkt URL ise
        if stdout.startswith(
            (
                "http://",
                "https://",
            )
        ):

            return clean_link(
                stdout
            )

        print(
            "Çözüm sonucunda HTTPS bulunamadı."
        )

        return None

    except FileNotFoundError:

        print()

        print(
            "HATA: hpwnr bulunamadı!"
        )

        print(
            "GitHub Actions içindeki "
            "hpwnr kurulumunu kontrol et."
        )

        return None

    except subprocess.TimeoutExpired:

        print(
            "hpwnr zaman aşımına uğradı."
        )

        return None

    except Exception as error:

        print(
            f"HAPP çözme hatası: {error}"
        )

        return None


# ============================================================
# BASE64 ÇÖZ
# ============================================================

def try_base64_decode(text):

    text = text.strip()

    if not text:

        return text

    try:

        decoded = base64.b64decode(
            text
            + "="
            * (-len(text) % 4),
            validate=False,
        )

        decoded_text = decoded.decode(
            "utf-8",
            errors="ignore",
        )

        if "://" in decoded_text:

            return decoded_text

    except Exception:

        pass

    return text


# ============================================================
# HTTPS ABONELİĞİNİ OKU
# ============================================================

def get_subscription(url):

    print()

    print("-" * 60)

    print(
        "HTTPS ABONELİĞİ AÇILIYOR"
    )

    print("-" * 60)

    print(
        url
    )

    try:

        content = http_get(
            url
        )

        print(
            f"İndirilen veri: "
            f"{len(content)} karakter"
        )

        # Önce direkt VPN linkleri
        links = VPN_PATTERN.findall(
            content
        )

        if links:

            print(
                "Doğrudan bulunan VPN linki: "
                f"{len(links)}"
            )

            return links

        # Base64 dene
        decoded = try_base64_decode(
            content
        )

        if decoded != content:

            links = VPN_PATTERN.findall(
                decoded
            )

            if links:

                print(
                    "Base64 çözüldükten sonra "
                    "bulunan VPN linki: "
                    f"{len(links)}"
                )

                return links

        print(
            "Bu HTTPS içinde VPN linki bulunamadı."
        )

        return []

    except urllib.error.HTTPError as error:

        print(
            f"HTTP hatası: {error.code}"
        )

        return []

    except urllib.error.URLError as error:

        print(
            f"Bağlantı hatası: {error}"
        )

        return []

    except Exception as error:

        print(
            f"Abonelik okuma hatası: {error}"
        )

        return []


# ============================================================
# TEK CRYPT5 LİNKİNİ İŞLE
# ============================================================

def process_happ_link(happ_link):

    resolved_url = decrypt_happ(
        happ_link
    )

    if not resolved_url:

        return []

    if not resolved_url.startswith(
        (
            "http://",
            "https://",
        )
    ):

        print(
            "Çözülmüş değer HTTPS değil."
        )

        return []

    return get_subscription(
        resolved_url
    )


# ============================================================
# ANA İŞLEM
# ============================================================

def main():

    print()

    print("=" * 60)

    print(
        "SADECE EN YENİ "
        "HAPP://CRYPT5 -> HTTPS -> VPN"
    )

    print("=" * 60)

    # ========================================================
    # 0. names.txt KONTROLÜ
    # ========================================================

    if not NAMES:

        print()

        print(
            "names.txt içinde kullanılabilir "
            "isim yok."
        )

        print(
            "Toplanan_linkler.txt DEĞİŞTİRİLMEDİ."
        )

        return

    # ========================================================
    # 1. SADECE EN YENİ CRYPT5
    # ========================================================

    latest_happ = (
        get_latest_crypt5_from_all_channels()
    )

    if not latest_happ:

        print()

        print(
            "CRYPT5 bulunamadı."
        )

        print(
            "Toplanan_linkler.txt "
            "DEĞİŞTİRİLMEDİ."
        )

        return

    # ========================================================
    # 2. SADECE O CRYPT5'İ ÇÖZ
    # ========================================================

    vpn_links = process_happ_link(
        latest_happ
    )

    # Yeni crypt5 çalışmazsa eski
    # çalışan listeyi koru.
    if not vpn_links:

        print()

        print(
            "Yeni CRYPT5'ten VPN linki alınamadı."
        )

        print(
            "Toplanan_linkler.txt "
            "DEĞİŞTİRİLMEDİ."
        )

        return

    # ========================================================
    # 3. DUPLICATE TEMİZLE
    # ========================================================

    all_vpn_links = []

    for link in vpn_links:

        link = clean_link(
            link
        )

        if link not in all_vpn_links:

            all_vpn_links.append(
                link
            )

    print()

    print("=" * 60)

    print(
        "YENİ VPN LINK SAYISI: "
        f"{len(all_vpn_links)}"
    )

    print("=" * 60)

    # ========================================================
    # 4. names.txt'DEKİ İSİMLERİ SIRAYLA EKLE
    # ========================================================

    processed_links = []

    for index, link in enumerate(
        all_vpn_links
    ):

        name = NAMES[
            index % len(NAMES)
        ]

        # Eski #etiketi varsa kaldır
        link = link.split(
            "#",
            1,
        )[0]

        final_link = (
            f"{link}#{name}"
        )

        processed_links.append(
            final_link
        )

    # ========================================================
    # 5. ESKİ DOSYAYI TAMAMEN DEĞİŞTİR
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        for link in processed_links:

            file.write(
                link
            )

            file.write(
                "\n"
            )

    # ========================================================
    # 6. SONUÇ
    # ========================================================

    print()

    print("=" * 60)

    print(
        "İŞLEM TAMAMLANDI"
    )

    print("=" * 60)

    print(
        f"Kullanılan HAPP: "
        f"{latest_happ}"
    )

    print(
        "Eski VPN listesi silindi."
    )

    print(
        "Yeni VPN listesi yazıldı."
    )

    print(
        f"Toplam VPN linki: "
        f"{len(processed_links)}"
    )

    print(
        f"Kullanılan isim sayısı: "
        f"{len(NAMES)}"
    )

    print(
        f"Çıktı dosyası: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 60)


# ============================================================
# ÇALIŞTIR
# ============================================================

if __name__ == "__main__":

    main()
