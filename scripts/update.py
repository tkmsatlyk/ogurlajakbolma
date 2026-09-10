import base64
import html
import re
import ssl
import subprocess
import urllib.request
from html.parser import HTMLParser
from datetime import datetime


# ============================================================
# AYARLAR
# ============================================================

CHANNELS = [
    "https://t.me/s/Richman_vpns",
    "https://t.me/s/expensive_vpn",
    "https://t.me/s/aron58",
    "https://t.me/topserverss",
]

OUTPUT_FILE = "Toplanan_linkler.txt"
NAMES_FILE = "names.txt"

MAX_MESSAGES_TO_SCAN = 100


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Linux; Android 10) "
        "AppleWebKit/537.36 "
        "Chrome/120.0.0.0 "
        "Mobile Safari/537.36"
    )
}


# ============================================================
# PATTERNLER
# ============================================================

CRYPT5_PATTERN = re.compile(
    r"happ://crypt5/[^\s<>\"']+",
    re.IGNORECASE,
)


HTTP_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)


VPN_PATTERN = re.compile(
    r"(?:"
    r"vless://[^\s<>\"']+"
    r"|vmess://[^\s<>\"']+"
    r"|trojan://[^\s<>\"']+"
    r"|ss://[^\s<>\"']+"
    r"|ssr://[^\s<>\"']+"
    r"|tuic://[^\s<>\"']+"
    r"|hysteria://[^\s<>\"']+"
    r"|hysteria2://[^\s<>\"']+"
    r"|hy2://[^\s<>\"']+"
    r"|socks://[^\s<>\"']+"
    r"|socks5://[^\s<>\"']+"
    r")",
    re.IGNORECASE,
)


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def clean_link(link):

    link = html.unescape(link)
    link = link.strip()

    return link.rstrip(
        ".,;:!?)]}'\"<>"
    )


def unique_links(links):

    result = []
    seen = set()

    for link in links:

        if not link:
            continue

        link = clean_link(link)

        if link and link not in seen:

            seen.add(link)
            result.append(link)

    return result


def extract_vpn_links(text):

    if not text:
        return []

    return unique_links(
        VPN_PATTERN.findall(text)
    )


# ============================================================
# HTTP GET
# ============================================================

def http_get(
    url,
    verify_ssl=True
):

    request = urllib.request.Request(
        url,
        headers=HEADERS,
    )

    context = None

    if not verify_ssl:

        context = ssl._create_unverified_context()

    with urllib.request.urlopen(
        request,
        timeout=30,
        context=context,
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
# BASE64 ÇÖZ
# ============================================================

def try_base64_decode(text):

    if not text:
        return None

    try:

        value = text.strip()

        decoded = base64.b64decode(
            value
            + "=" * (-len(value) % 4),
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

    return None


# ============================================================
# HTTPS / HTTP ABONELİK KONTROL
# ============================================================

def get_links_from_http(url):

    url = clean_link(url)

    print()
    print(
        "HTTPS/HTTP kontrol ediliyor:"
    )
    print(url)

    content = None

    for verify_ssl in (
        True,
        False
    ):

        try:

            content = http_get(
                url,
                verify_ssl=verify_ssl,
            )

            break

        except Exception as error:

            print(
                "Bağlantı hatası:",
                error,
            )

    if content is None:

        return []

    # --------------------------------------------------------
    # 1. DİREKT VPN LINKLERİ
    # --------------------------------------------------------

    direct_links = extract_vpn_links(
        content
    )

    if direct_links:

        print(
            "HTTP içinden VPN bulundu:",
            len(direct_links),
        )

        return direct_links

    # --------------------------------------------------------
    # 2. BASE64 ÇÖZ
    # --------------------------------------------------------

    decoded = try_base64_decode(
        content
    )

    if decoded:

        decoded_links = extract_vpn_links(
            decoded
        )

        if decoded_links:

            print(
                "Base64 içinden VPN bulundu:",
                len(decoded_links),
            )

            return decoded_links

    print(
        "Bu HTTP/HTTPS linki VPN içermiyor."
    )

    return []


# ============================================================
# HAPP CRYPT5 ÇÖZ
# ============================================================

def decrypt_happ(happ_link):

    print()
    print(
        "CRYPT5 çözülüyor:"
    )
    print(happ_link)

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

    except FileNotFoundError:

        print(
            "HATA: hpwnr bulunamadı."
        )

        return []

    except subprocess.TimeoutExpired:

        print(
            "hpwnr zaman aşımı."
        )

        return []

    output = (
        (result.stdout or "")
        + "\n"
        + (result.stderr or "")
    )

    if result.returncode != 0:

        print(
            "CRYPT5 çözme hatası:"
        )

        print(
            output.strip()
        )

        return []

    # --------------------------------------------------------
    # CRYPT5 ÇIKTISINDA DOĞRUDAN VPN
    # --------------------------------------------------------

    direct_vpn = extract_vpn_links(
        output
    )

    if direct_vpn:

        print(
            "CRYPT5 içinden direkt VPN bulundu:",
            len(direct_vpn),
        )

        return direct_vpn

    # --------------------------------------------------------
    # CRYPT5 ÇIKTISINDA HTTP / HTTPS
    # --------------------------------------------------------

    urls = unique_links(
        HTTP_PATTERN.findall(output)
    )

    all_links = []

    for url in urls:

        links = get_links_from_http(
            url
        )

        all_links.extend(
            links
        )

    return unique_links(
        all_links
    )


# ============================================================
# TELEGRAM PARSER
# ============================================================

class TelegramMessageParser(HTMLParser):

    def __init__(self):

        super().__init__(
            convert_charrefs=True
        )

        self.depth = 0

        self.current = None

        self.messages = []


    def handle_starttag(
        self,
        tag,
        attrs,
    ):

        attrs = dict(attrs)

        if tag == "div":

            classes = attrs.get(
                "class",
                "",
            ).split()

            if (
                self.depth == 0
                and "tgme_widget_message"
                in classes
            ):

                self.depth = 1

                self.current = {
                    "datetime": None,
                    "text": "",
                    "vpn": [],
                    "crypt5": [],
                    "http": [],
                }

                return

            if self.depth > 0:

                self.depth += 1

        # ----------------------------------------------------
        # TARİH
        # ----------------------------------------------------

        if (
            self.depth > 0
            and tag == "time"
            and self.current
        ):

            value = attrs.get(
                "datetime"
            )

            if (
                value
                and not self.current[
                    "datetime"
                ]
            ):

                self.current[
                    "datetime"
                ] = value

        # ----------------------------------------------------
        # ATTRIBUTELERDE LINK ARA
        # ----------------------------------------------------

        if (
            self.depth > 0
            and self.current
        ):

            for value in attrs.values():

                if value:

                    self.find_links(
                        value
                    )


    def handle_data(
        self,
        data,
    ):

        if (
            self.depth > 0
            and self.current
        ):

            self.current[
                "text"
            ] += data

            self.find_links(
                data
            )


    def find_links(
        self,
        text,
    ):

        if not self.current:

            return

        # VPN

        for link in extract_vpn_links(
            text
        ):

            if (
                link
                not in self.current[
                    "vpn"
                ]
            ):

                self.current[
                    "vpn"
                ].append(
                    link
                )

        # CRYPT5

        for link in CRYPT5_PATTERN.findall(
            text
        ):

            link = clean_link(
                link
            )

            if (
                link
                not in self.current[
                    "crypt5"
                ]
            ):

                self.current[
                    "crypt5"
                ].append(
                    link
                )

        # HTTP / HTTPS

        for link in HTTP_PATTERN.findall(
            text
        ):

            link = clean_link(
                link
            )

            # Telegram sayfasını tekrar
            # abonelik gibi işlemeye çalışma.

            if "t.me/" in link.lower():

                continue

            if (
                link
                not in self.current[
                    "http"
                ]
            ):

                self.current[
                    "http"
                ].append(
                    link
                )


    def handle_endtag(
        self,
        tag,
    ):

        if (
            self.depth <= 0
            or tag != "div"
        ):

            return

        self.depth -= 1

        if (
            self.depth == 0
            and self.current
        ):

            self.messages.append(
                self.current
            )

            self.current = None


# ============================================================
# TARİH ÇÖZ
# ============================================================

def parse_datetime(value):

    if not value:

        return None

    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError:

        return None


# ============================================================
# KANAL MESAJLARINI AL
# ============================================================

def get_channel_messages(channel):

    print()
    print(
        "=" * 70
    )

    print(
        "KANAL:"
    )

    print(
        channel
    )

    print(
        "=" * 70
    )

    content = None

    for verify_ssl in (
        True,
        False
    ):

        try:

            content = http_get(
                channel,
                verify_ssl=verify_ssl,
            )

            break

        except Exception as error:

            print(
                "Kanal bağlantı hatası:",
                error,
            )

    if content is None:

        return False, []

    parser = TelegramMessageParser()

    parser.feed(
        content
    )

    messages = parser.messages

    dated = []

    for message in messages:

        dt = parse_datetime(
            message.get(
                "datetime"
            )
        )

        if dt:

            dated.append(
                (
                    dt,
                    message,
                )
            )

    if dated:

        dated.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        messages = [
            item[1]
            for item in dated
        ]

    else:

        messages = list(
            reversed(
                messages
            )
        )

    print(
        "Bulunan mesaj:",
        len(messages),
    )

    return True, messages


# ============================================================
# BİR KANALI İŞLE
# ============================================================

def process_channel(channel):

    success, messages = (
        get_channel_messages(
            channel
        )
    )

    if not success:

        return False, []

    print()
    print(
        "EN YENİ MESAJDAN BAŞLAYARAK TARAMA..."
    )

    for index, message in enumerate(
        messages[
            :MAX_MESSAGES_TO_SCAN
        ],
        start=1,
    ):

        print()
        print(
            "-" * 60
        )

        print(
            f"MESAJ {index} KONTROL EDİLİYOR"
        )

        print(
            "-" * 60
        )

        # ----------------------------------------------------
        # 1. DOĞRUDAN VPN
        # ----------------------------------------------------

        direct_vpn = unique_links(
            message.get(
                "vpn",
                [],
            )
        )

        if direct_vpn:

            print(
                "DOĞRUDAN VPN BULUNDU:"
            )

            print(
                len(direct_vpn)
            )

            return True, direct_vpn

        # ----------------------------------------------------
        # 2. HAPP CRYPT5
        # ----------------------------------------------------

        crypt5_links = unique_links(
            message.get(
                "crypt5",
                [],
            )
        )

        if crypt5_links:

            print(
                "CRYPT5 bulundu."
            )

            all_links = []

            for crypt5 in crypt5_links:

                links = decrypt_happ(
                    crypt5
                )

                all_links.extend(
                    links
                )

            all_links = unique_links(
                all_links
            )

            if all_links:

                print(
                    "CRYPT5 içinden VPN bulundu:",
                    len(all_links),
                )

                return True, all_links

            print(
                "CRYPT5 çalışmadı veya VPN vermedi."
            )

        # ----------------------------------------------------
        # 3. HTTP / HTTPS
        # ----------------------------------------------------

        http_links = unique_links(
            message.get(
                "http",
                [],
            )
        )

        if http_links:

            print(
                "HTTP/HTTPS linkleri kontrol ediliyor."
            )

            all_links = []

            for url in http_links:

                links = get_links_from_http(
                    url
                )

                all_links.extend(
                    links
                )

            all_links = unique_links(
                all_links
            )

            if all_links:

                print(
                    "HTTPS içinden VPN bulundu:",
                    len(all_links),
                )

                return True, all_links

            print(
                "HTTPS linkleri VPN içermiyor."
            )

        # ----------------------------------------------------
        # HİÇBİR ŞEY YOK
        # ----------------------------------------------------

        print(
            "VPN/CRYPT5/geçerli HTTPS yok."
        )

        print(
            "Eski mesaja geçiliyor..."
        )

    print()
    print(
        "Bu kanalda kullanılabilir"
        " VPN mesajı bulunamadı."
    )

    return True, []


# ============================================================
# NAMES.TXT OKU
# ============================================================

def load_names():

    try:

        with open(
            NAMES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            names = [
                line.strip()
                for line in file
                if line.strip()
            ]

        print(
            "İsim sayısı:",
            len(names),
        )

        return names

    except FileNotFoundError:

        print(
            "HATA: names.txt bulunamadı!"
        )

        return []


# ============================================================
# ANA PROGRAM
# ============================================================

def main():

    print()
    print(
        "=" * 70
    )

    print(
        "TELEGRAM VPN TOPLAYICI"
    )

    print(
        "VPN + CRYPT5 + HTTPS + BASE64"
    )

    print(
        "=" * 70
    )

    names = load_names()

    if not names:

        print(
            "İsimler yüklenemedi."
        )

        return

    all_links = []

    successful_channels = 0

    # --------------------------------------------------------
    # TÜM KANALLAR
    # --------------------------------------------------------

    for channel in CHANNELS:

        success, links = process_channel(
            channel
        )

        if success:

            successful_channels += 1

        for link in unique_links(
            links
        ):

            if link not in all_links:

                all_links.append(
                    link
                )

    # --------------------------------------------------------
    # HİÇ KANAL OKUNAMADIYSA
    # --------------------------------------------------------

    if successful_channels == 0:

        print()
        print(
            "Hiçbir kanal okunamadı."
        )

        print(
            "Eski çıktı korunuyor."
        )

        return

    # --------------------------------------------------------
    # ÇIKTI
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "TOPLAM VPN LİNKİ:",
        len(all_links),
    )

    print(
        "=" * 70
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        for index, link in enumerate(
            all_links
        ):

            # Eski #isim varsa kaldır

            link = link.split(
                "#",
                1,
            )[0]

            # İsim seç

            if index < len(names):

                name = names[index]

            else:

                name = (
                    f"VPN {index + 1}"
                )

            file.write(
                f"{link}#{name}\n"
            )

    print()
    print(
        "TAMAMLANDI"
    )

    print(
        "Çıktı dosyası:",
        OUTPUT_FILE,
    )

    print(
        "Toplam link:",
        len(all_links),
    )


# ============================================================
# ÇALIŞTIR
# ============================================================

if __name__ == "__main__":

    main()
