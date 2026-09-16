import base64
import html
import re
import ssl
import subprocess
import urllib.request
from html.parser import HTMLParser
from datetime import datetime


# ============================================================
# KANALLAR
# ============================================================

CHANNELS = [
    "https://t.me/s/Richman_vpns",
    "https://t.me/s/expensive_vpn",
    "https://t.me/s/aron58",
    "https://t.me/s/topserverss",
    "https://t.me/s/star_vpns",
    "https://t.me/s/v2speed_vpns",
    "https://t.me/s/ares_happ",
    "https://t.me/s/happvpn",
    "https://t.me/s/tiktok1server",
]

OUTPUT_FILE = "Toplanan_linkler.txt"
NAMES_FILE = "names.txt"

# Her kanalda en fazla kaç mesaj geriye bakılacak?
MAX_MESSAGES_TO_SCAN = 100


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 "
        "Mobile Safari/537.36"
    )
}


# ============================================================
# DESTEKLENEN VPN PROTOKOLLERİ
# ============================================================

VPN_PATTERN = re.compile(
    r"(?:"
    r"vless://[^\s<>'\"]+"
    r"|vmess://[^\s<>'\"]+"
    r"|trojan://[^\s<>'\"]+"
    r"|ss://[^\s<>'\"]+"
    r"|ssr://[^\s<>'\"]+"
    r"|tuic://[^\s<>'\"]+"
    r"|hysteria://[^\s<>'\"]+"
    r"|hysteria2://[^\s<>'\"]+"
    r"|hy2://[^\s<>'\"]+"
    r"|socks://[^\s<>'\"]+"
    r"|socks5://[^\s<>'\"]+"
    r")",
    re.IGNORECASE,
)


CRYPT5_PATTERN = re.compile(
    r"happ://crypt5/[^\s<>'\"]+",
    re.IGNORECASE,
)


HTTP_PATTERN = re.compile(
    r"https?://[^\s<>'\"]+",
    re.IGNORECASE,
)


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def clean_link(link):
    if not link:
        return ""

    return html.unescape(
        str(link)
    ).strip().rstrip(
        ".,;:!?)]}'\"<>"
    )


def unique_links(links):
    result = []
    seen = set()

    for link in links or []:
        link = clean_link(link)

        if not link:
            continue

        if link not in seen:
            seen.add(link)
            result.append(link)

    return result


def extract_direct_vpn(text):
    """
    Metnin içindeki bütün doğrudan VPN URI'lerini bulur.
    """

    if not text:
        return []

    return unique_links(
        VPN_PATTERN.findall(
            str(text)
        )
    )


def extract_http_urls(text):
    """
    Metnin içindeki bütün HTTP/HTTPS URL'lerini bulur.
    """

    if not text:
        return []

    return unique_links(
        HTTP_PATTERN.findall(
            str(text)
        )
    )


def is_http_url(url):
    url = clean_link(url).lower()

    return (
        url.startswith("http://")
        or url.startswith("https://")
    )


# ============================================================
# HTTP
# ============================================================

def http_get(
    url,
    verify_ssl=True,
    timeout=30
):
    request = urllib.request.Request(
        url,
        headers=HEADERS
    )

    context = None

    if not verify_ssl:
        context = ssl._create_unverified_context()

    with urllib.request.urlopen(
        request,
        timeout=timeout,
        context=context
    ) as response:

        data = response.read()

        charset = (
            response.headers.get_content_charset()
            or "utf-8"
        )

        return data.decode(
            charset,
            errors="ignore"
        )


def http_get_with_fallback(
    url,
    timeout=30
):
    """
    Önce normal SSL ile dener.
    Sertifika sorunu varsa SSL doğrulamasını
    kapatıp tekrar dener.
    """

    try:
        return http_get(
            url,
            verify_ssl=True,
            timeout=timeout
        )

    except Exception as error:
        print(
            "Normal bağlantı başarısız:",
            error
        )

    try:
        content = http_get(
            url,
            verify_ssl=False,
            timeout=timeout
        )

        print(
            "SSL doğrulaması kapatılarak bağlantı başarılı."
        )

        return content

    except Exception as error:
        print(
            "SSL kapalı bağlantı da başarısız:",
            error
        )

        return None


# ============================================================
# TARİH
# ============================================================

def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

    except (
        ValueError,
        TypeError
    ):
        return None


# ============================================================
# TELEGRAM HTML PARSER
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
        attrs
    ):
        attrs_dict = dict(attrs)

        # Yeni Telegram mesajı
        if tag == "div":

            classes = attrs_dict.get(
                "class",
                ""
            ).split()

            if (
                self.depth == 0
                and "tgme_widget_message" in classes
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

        # Mesaj tarihi
        if (
            self.depth > 0
            and tag == "time"
            and self.current
        ):

            value = attrs_dict.get(
                "datetime"
            )

            if (
                value
                and not self.current["datetime"]
            ):
                self.current["datetime"] = value

        # href / data-* gibi attribute'ları da kontrol et
        if (
            self.depth > 0
            and self.current
        ):

            for value in attrs_dict.values():

                if value:
                    self.find_links(value)

    def handle_data(self, data):

        if (
            self.depth > 0
            and self.current
        ):

            self.current["text"] += data

            self.find_links(data)

    def find_links(self, text):

        if (
            not self.current
            or not text
        ):
            return

        # Direct VPN
        for link in VPN_PATTERN.findall(text):

            link = clean_link(link)

            if link not in self.current["vpn"]:
                self.current["vpn"].append(link)

        # crypt5
        for link in CRYPT5_PATTERN.findall(text):

            link = clean_link(link)

            if link not in self.current["crypt5"]:
                self.current["crypt5"].append(link)

        # HTTP / HTTPS
        for link in HTTP_PATTERN.findall(text):

            link = clean_link(link)

            if link not in self.current["http"]:
                self.current["http"].append(link)

    def handle_endtag(self, tag):

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
# TELEGRAM KANALINI OKU
# ============================================================

def get_channel_messages(channel):

    print()
    print("=" * 70)
    print("KANAL:", channel)
    print("=" * 70)

    content = http_get_with_fallback(
        channel
    )

    if content is None:

        print(
            "Kanal okunamadı."
        )

        return False, []

    parser = TelegramMessageParser()

    try:
        parser.feed(content)

    except Exception as error:

        print(
            "Telegram HTML ayrıştırma hatası:",
            error
        )

        return True, []

    if not parser.messages:

        print(
            "Telegram mesajı bulunamadı."
        )

        return True, []

    dated = []

    for message in parser.messages:

        dt = parse_datetime(
            message.get(
                "datetime"
            )
        )

        if dt:
            dated.append(
                (
                    dt,
                    message
                )
            )

    # Tarihli mesajları en yeni -> eski sırala
    if dated:

        dated.sort(
            key=lambda item: item[0],
            reverse=True
        )

        messages = [
            item[1]
            for item in dated
        ]

    else:

        messages = list(
            reversed(
                parser.messages
            )
        )

    print(
        "Bulunan mesaj:",
        len(messages)
    )

    return True, messages


# ============================================================
# HPWNR
# ============================================================

def run_hpwnr(
    args,
    timeout=90
):
    """
    hpwnr komutunu çalıştırır.
    """

    try:

        result = subprocess.run(
            ["hpwnr"] + list(args),
            capture_output=True,
            text=True,
            timeout=timeout
        )

    except FileNotFoundError:

        print(
            "HATA: hpwnr bulunamadı."
        )

        return None

    except subprocess.TimeoutExpired:

        print(
            "hpwnr zaman aşımı."
        )

        return None

    except Exception as error:

        print(
            "hpwnr çalıştırma hatası:",
            error
        )

        return None

    output = (
        (result.stdout or "")
        + "\n"
        + (result.stderr or "")
    )

    if result.returncode != 0:

        print(
            "hpwnr hata verdi:",
            output.strip()
        )

        return None

    return output


# ============================================================
# CRYPT5 ÇÖZ
# ============================================================

def decrypt_happ(happ_link):

    print(
        "CRYPT5 çözülüyor:",
        happ_link
    )

    output = run_hpwnr(
        [happ_link],
        timeout=60
    )

    if output is None:
        return ""

    return output


# ============================================================
# BASE64
# ============================================================

def try_base64_decode(text):

    if not text:
        return None

    stripped = text.strip()

    if not stripped:
        return None

    # Satır sonlarını / boşlukları kaldır
    compact = re.sub(
        r"\s+",
        "",
        stripped
    )

    if len(compact) < 8:
        return None

    try:

        padded = (
            compact
            + "=" * (
                -len(compact) % 4
            )
        )

        decoded = base64.b64decode(
            padded,
            validate=False
        )

        value = decoded.decode(
            "utf-8",
            errors="ignore"
        )

        # Gerçekten VPN çıktıysa kabul et
        if extract_direct_vpn(value):

            return value

    except Exception:
        pass

    return None


# ============================================================
# SUBSCRIPTION OKU
# ============================================================

def get_subscription(url):
    """
    Sistem burada otomatik karar verir:

    DIRECT VPN var mı?
        EVET -> bütün VPN'leri al

        HAYIR
          ↓
        Base64 mı?
          EVET -> decode et -> VPN'leri al

          HAYIR
            ↓
        Geçersiz -> eski Telegram mesajına dön
    """

    url = clean_link(url)

    if not is_http_url(url):
        return []

    print()
    print(
        "Abonelik okunuyor:",
        url
    )

    # --------------------------------------------------------
    # 1. hpwnr uri
    # --------------------------------------------------------

    output = run_hpwnr(
        [
            url,
            "uri"
        ],
        timeout=90
    )

    if output:

        direct = extract_direct_vpn(
            output
        )

        if direct:

            print(
                "hpwnr ile doğrudan VPN bulundu:",
                len(direct)
            )

            return direct

    # --------------------------------------------------------
    # 2. HTTP ile indir
    # --------------------------------------------------------

    content = http_get_with_fallback(
        url,
        timeout=30
    )

    if content is None:
        return []

    # --------------------------------------------------------
    # 3. ÖNCE DIRECT VPN KONTROLÜ
    # --------------------------------------------------------

    direct = extract_direct_vpn(
        content
    )

    if direct:

        print(
            "Abonelik içinde doğrudan VPN bulundu:",
            len(direct)
        )

        return direct

    # --------------------------------------------------------
    # 4. DIRECT YOKSA BASE64
    # --------------------------------------------------------

    decoded = try_base64_decode(
        content
    )

    if decoded:

        direct = extract_direct_vpn(
            decoded
        )

        if direct:

            print(
                "Base64 içinden VPN bulundu:",
                len(direct)
            )

            return direct

    # --------------------------------------------------------
    # 5. HİÇBİR ŞEY YOK
    # --------------------------------------------------------

    print(
        "Abonelikte kullanılabilir VPN bulunamadı."
    )

    return []


# ============================================================
# CRYPT5 ÇIKTISINI İŞLE
# ============================================================

def process_resolved_crypt5_output(
    output
):
    """
    crypt5 çözüldükten sonra:

    1. Direct VPN varsa hepsini al.
    2. Direct VPN yoksa HTTP/HTTPS subscription bul.
    3. Subscription -> direct veya Base64.
    """

    if not output:
        return []

    # --------------------------------------------------------
    # 1. DIRECT VPN
    # --------------------------------------------------------

    direct = extract_direct_vpn(
        output
    )

    if direct:

        print(
            "CRYPT5 içinden doğrudan VPN sayısı:",
            len(direct)
        )

        return direct

    # --------------------------------------------------------
    # 2. HTTP / HTTPS
    # --------------------------------------------------------

    subscription_urls = extract_http_urls(
        output
    )

    if not subscription_urls:
        return []

    print(
        "CRYPT5 içinden abonelik URL sayısı:",
        len(subscription_urls)
    )

    all_links = []

    for url in subscription_urls:

        links = get_subscription(
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
            "CRYPT5 içinden toplam VPN:",
            len(all_links)
        )

    return all_links


# ============================================================
# TEK MESAJI İŞLE
# ============================================================

def process_message(message):
    """
    Bir Telegram mesajında:

    1. Direct VPN
    2. crypt5
    3. HTTP/HTTPS subscription

    kontrol edilir.

    Kullanılabilir VPN bulunursa o mesajdan
    çıkan TÜM VPN linkleri döndürülür.
    """

    # ========================================================
    # 1. DIRECT VPN
    # ========================================================

    direct = unique_links(
        message.get(
            "vpn",
            []
        )
    )

    if direct:

        print(
            "Mesaj içinde doğrudan VPN bulundu:",
            len(direct)
        )

        return direct

    # ========================================================
    # 2. CRYPT5
    # ========================================================

    crypt5_links = unique_links(
        message.get(
            "crypt5",
            []
        )
    )

    if crypt5_links:

        crypt5_result = []

        for crypt5 in crypt5_links:

            output = decrypt_happ(
                crypt5
            )

            if not output:
                continue

            crypt5_result.extend(
                process_resolved_crypt5_output(
                    output
                )
            )

        crypt5_result = unique_links(
            crypt5_result
        )

        if crypt5_result:
            return crypt5_result

    # ========================================================
    # 3. HTTP / HTTPS SUBSCRIPTION
    # ========================================================

    subscription_urls = unique_links(
        message.get(
            "http",
            []
        )
    )

    if subscription_urls:

        subscription_result = []

        for url in subscription_urls:

            subscription_result.extend(
                get_subscription(
                    url
                )
            )

        subscription_result = unique_links(
            subscription_result
        )

        if subscription_result:

            return subscription_result

    # ========================================================
    # KULLANILABİLİR VPN YOK
    # ========================================================

    return []


# ============================================================
# TEK KANALI İŞLE
# ============================================================

def process_channel(channel):
    """
    SADECE BU KANALI tarar.

    En yeni kullanılabilir mesaj bulunduğunda
    o kanalın taraması durur.

    FAKAT ana program DURMAZ.

    main() sonraki kanala geçer.
    """

    success, messages = get_channel_messages(
        channel
    )

    if not success:
        return False, []

    scan_count = min(
        len(messages),
        MAX_MESSAGES_TO_SCAN
    )

    # --------------------------------------------------------
    # EN YENİDEN ESKİYE
    # --------------------------------------------------------

    for index in range(
        scan_count
    ):

        message = messages[index]

        print()
        print(
            f"Mesaj {index + 1}/{scan_count} "
            f"kontrol ediliyor..."
        )

        links = process_message(
            message
        )

        # ====================================================
        # BU KANALDA KULLANILABİLİR PAYLAŞIM BULUNDU
        # ====================================================

        if links:

            print()
            print(
                "Bu kanaldaki EN YENİ "
                "kullanılabilir paylaşım bulundu."
            )

            print(
                "Bu kanaldan alınan VPN:",
                len(links)
            )

            # SADECE BU KANALIN taraması bitiyor.
            #
            # main() BURADAN SONRA
            # sonraki kanala devam edecek.
            return True, unique_links(
                links
            )

        print(
            "Kullanılabilir VPN yok "
            "-> eski mesaja geçiliyor."
        )

    print()
    print(
        "Bu kanalda kullanılabilir VPN bulunamadı."
    )

    return True, []


# ============================================================
# NAMES.TXT
# ============================================================

def load_names():

    try:

        with open(
            NAMES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return [
                line.strip()
                for line in file
                if line.strip()
            ]

    except FileNotFoundError:

        print(
            "UYARI: names.txt bulunamadı."
            " Linkler yine toplanacak."
        )

        return []


# ============================================================
# ÇIKTI DOSYASI
# ============================================================

def write_output(
    all_links,
    names
):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for index, link in enumerate(
            all_links
        ):

            # Eski #isim kısmını kaldır
            link = link.split(
                "#",
                1
            )[0]

            if index < len(names):

                name = names[index]

            else:

                name = f"VPN {index + 1}"

            file.write(
                f"{link}#{name}\n"
            )


# ============================================================
# ANA PROGRAM
# ============================================================

def main():

    print("=" * 70)

    print(
        "TÜM KANALLARI TARAYAN VPN TOPLAYICI"
    )

    print("=" * 70)

    names = load_names()

    all_links = []

    successful_channels = 0

    total_channels = len(
        CHANNELS
    )

    # ========================================================
    # ÇOK ÖNEMLİ:
    #
    # BURADA BREAK YOK.
    #
    # Bir kanaldan VPN bulunsa bile
    # for döngüsü sonraki kanala geçer.
    # ========================================================

    for channel_index, channel in enumerate(
        CHANNELS,
        1
    ):

        print()
        print(
            f">>> KANAL "
            f"{channel_index}/{total_channels}"
        )

        try:

            success, links = process_channel(
                channel
            )

        except Exception as error:

            # Bir kanal hata verirse
            # diğer kanallar devam eder.

            print(
                "KANAL HATASI:",
                error
            )

            success = False
            links = []

        if success:

            successful_channels += 1

        # ----------------------------------------------------
        # Bu kanaldan gelen bütün linkleri genel listeye ekle
        # ----------------------------------------------------

        for link in unique_links(
            links
        ):

            if link not in all_links:

                all_links.append(
                    link
                )

        print()
        print(
            f">>> Kanal {channel_index} tamamlandı."
        )

        print(
            ">>> Sonraki kanala geçiliyor..."
        )

    # ========================================================
    # BÜTÜN KANALLAR BİTTİ
    # ========================================================

    print()
    print("=" * 70)

    print(
        "BÜTÜN KANALLAR TARANDI"
    )

    print("=" * 70)

    print(
        "Okunabilen kanal:",
        successful_channels,
        "/",
        total_channels
    )

    print(
        "Toplam benzersiz VPN:",
        len(all_links)
    )

    # ========================================================
    # HİÇBİR KANAL OKUNMADIYSA ESKİ ÇIKTIYI KORU
    # ========================================================

    if successful_channels == 0:

        print(
            "Hiçbir kanal okunamadı."
            " Mevcut çıktı korunuyor."
        )

        return

    # ========================================================
    # GÜNCEL ÇIKTI
    # ========================================================

    write_output(
        all_links,
        names
    )

    print()
    print(
        "Çıktı:",
        OUTPUT_FILE
    )

    print("=" * 70)


# ============================================================
# BAŞLAT
# ============================================================

if __name__ == "__main__":
    main()
