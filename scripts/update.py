import base64
import html
import re
import ssl
import subprocess
import urllib.request
import urllib.error
from html.parser import HTMLParser
from datetime import datetime

CHANNELS = [
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
    "https://t.me/s/happvpn",
    "https://t.me/s/expensive_vpn",
    "https://t.me/s/aron58",
]

OUTPUT_FILE = "Toplanan_linkler.txt"
NAMES_FILE = "names.txt"
MAX_MESSAGES_TO_SCAN = 100

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
}

CRYPT5_PATTERN = re.compile(r'happ://crypt5/[^\s<>"\']+', re.I)
SS_PATTERN = re.compile(r'ss://[^\s<>"\']+', re.I)

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
    re.I,
)


def clean_link(link):
    return html.unescape(link).strip().rstrip('.,;:!?)]}\'"<>'):


def unique_links(links):
    result = []
    seen = set()

    for link in links or []:
        link = clean_link(link)

        if link and link not in seen:
            seen.add(link)
            result.append(link)

    return result


def http_get(url, verify_ssl=True):
    request = urllib.request.Request(
        url,
        headers=HEADERS
    )

    context = None

    if not verify_ssl:
        context = ssl._create_unverified_context()

    with urllib.request.urlopen(
        request,
        timeout=30,
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


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


class TelegramMessageParser(HTMLParser):

    def __init__(self):
        super().__init__(
            convert_charrefs=True
        )

        self.depth = 0
        self.current = None
        self.messages = []

    def handle_starttag(self, tag, attrs):

        attrs = dict(attrs)

        if tag == "div":

            classes = attrs.get(
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
                    "ss": [],
                    "crypt5": [],
                }

                return

            if self.depth > 0:
                self.depth += 1

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
                and not self.current["datetime"]
            ):

                self.current["datetime"] = value

        if self.depth > 0 and self.current:

            for value in attrs.values():

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

        if not self.current:
            return

        for link in SS_PATTERN.findall(text):

            link = clean_link(link)

            if link not in self.current["ss"]:

                self.current["ss"].append(link)

        for link in CRYPT5_PATTERN.findall(text):

            link = clean_link(link)

            if link not in self.current["crypt5"]:

                self.current["crypt5"].append(link)

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


def get_channel_messages(channel):

    print()
    print("=" * 70)
    print("KANAL:", channel)
    print("=" * 70)

    try:

        content = http_get(channel)

    except Exception as error:

        print(
            "Normal bağlantı başarısız:",
            error
        )

        try:

            content = http_get(
                channel,
                verify_ssl=False
            )

            print(
                "SSL doğrulaması kapatılarak bağlantı başarılı."
            )

        except Exception as error2:

            print(
                "Kanal okunamadı:",
                error2
            )

            return False, []

    parser = TelegramMessageParser()

    parser.feed(content)

    if not parser.messages:

        print(
            "Telegram mesajı bulunamadı."
        )

        return True, []

    dated = []

    for message in parser.messages:

        dt = parse_datetime(
            message["datetime"]
        )

        if dt:

            dated.append(
                (dt, message)
            )

    if dated:

        dated.sort(
            key=lambda x: x[0],
            reverse=True
        )

        messages = [
            x[1]
            for x in dated
        ]

    else:

        messages = list(
            reversed(parser.messages)
        )

    print(
        "Bulunan mesaj:",
        len(messages)
    )

    return True, messages


def decrypt_happ(happ_link):

    print(
        "CRYPT5 çözülüyor:",
        happ_link
    )

    try:

        result = subprocess.run(
            [
                "hpwnr",
                happ_link
            ],
            capture_output=True,
            text=True,
            timeout=60
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
        result.stdout or ""
    ) + "\n" + (
        result.stderr or ""
    )

    if result.returncode != 0:

        print(
            "hpwnr hata verdi:",
            output.strip()
        )

        return []

    urls = re.findall(
        r'https?://[^\s<>"\']+',
        output,
        re.I
    )

    urls = unique_links(urls)

    if urls:

        print(
            "Çözülen abonelik URL sayısı:",
            len(urls)
        )

        return urls

    direct = unique_links(
        VPN_PATTERN.findall(output)
    )

    if direct:

        print(
            "CRYPT5 içinden doğrudan VPN sayısı:",
            len(direct)
        )

    return direct


def try_base64_decode(text):

    try:

        stripped = text.strip()

        decoded = base64.b64decode(
            stripped
            + "=" * (-len(stripped) % 4),
            validate=False
        )

        value = decoded.decode(
            "utf-8",
            errors="ignore"
        )

        if "://" in value:

            return value

    except Exception:

        pass

    return text


def get_subscription(url):

    print(
        "Abonelik okunuyor:",
        url
    )

    try:

        result = subprocess.run(
            [
                "hpwnr",
                url,
                "uri"
            ],
            capture_output=True,
            text=True,
            timeout=90
        )

        if result.returncode == 0:

            links = unique_links(
                VPN_PATTERN.findall(
                    result.stdout or ""
                )
            )

            if links:

                print(
                    "Bulunan VPN linki:",
                    len(links)
                )

                return links

    except Exception as error:

        print(
            "hpwnr uri hatası:",
            error
        )

    content = None

    for verify in (
        True,
        False
    ):

        try:

            content = http_get(
                url,
                verify_ssl=verify
            )

            if not verify:

                print(
                    "Abonelik SSL doğrulaması kapatılarak okundu."
                )

            break

        except Exception as error:

            print(
                "Abonelik bağlantı hatası:",
                error
            )

    if content is None:

        return []

    links = unique_links(
        VPN_PATTERN.findall(content)
    )

    if links:

        print(
            "HTTP içinden VPN linki:",
            len(links)
        )

        return links

    decoded = try_base64_decode(
        content
    )

    if decoded != content:

        links = unique_links(
            VPN_PATTERN.findall(decoded)
        )

        if links:

            print(
                "Base64 içinden VPN linki:",
                len(links)
            )

            return links

    print(
        "Abonelikte VPN linki bulunamadı."
    )

    return []


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
            "HATA: names.txt bulunamadı!"
        )

        return []


def process_channel(channel):

    success, messages = get_channel_messages(
        channel
    )

    if not success:

        return False, []

    # ========================================================
    # SADECE SS VE CRYPT5 ARANIYOR
    # Direkt vless/vmess/trojan vb. ALINMIYOR.
    # ========================================================

    for index, message in enumerate(
        messages[:MAX_MESSAGES_TO_SCAN],
        1
    ):

        print()
        print(
            "Mesaj",
            index,
            "kontrol ediliyor..."
        )

        # ----------------------------------------------------
        # 1. SS
        # ----------------------------------------------------

        ss_links = unique_links(
            message.get("ss", [])
        )

        if ss_links:

            print(
                "SS bulundu ->",
                len(ss_links),
                "link alındı."
            )

            return True, ss_links

        # ----------------------------------------------------
        # 2. HAPP://CRYPT5
        # ----------------------------------------------------

        crypt5_links = unique_links(
            message.get("crypt5", [])
        )

        if crypt5_links:

            for crypt5 in crypt5_links:

                resolved = decrypt_happ(
                    crypt5
                )

                if not resolved:

                    continue

                # Crypt5 doğrudan VPN URI döndürdüyse
                direct = unique_links([
                    x
                    for x in resolved
                    if isinstance(x, str)
                    and not x.lower().startswith(
                        (
                            "http://",
                            "https://"
                        )
                    )
                ])

                if direct:

                    return True, direct

                # Crypt5 HTTPS subscription döndürdüyse
                all_subscription_links = []

                for url in resolved:

                    if (
                        isinstance(url, str)
                        and url.lower().startswith(
                            (
                                "http://",
                                "https://"
                            )
                        )
                    ):

                        all_subscription_links.extend(
                            get_subscription(
                                clean_link(url)
                            )
                        )

                all_subscription_links = unique_links(
                    all_subscription_links
                )

                if all_subscription_links:

                    print(
                        "CRYPT5 içinden toplam VPN:",
                        len(all_subscription_links)
                    )

                    return True, all_subscription_links

        # ----------------------------------------------------
        # 3. Hiçbiri yoksa eski mesaja geç
        # ----------------------------------------------------

        print(
            "SS/CRYPT5 yok veya çalışmadı."
            " -> Eski mesaja geçiliyor."
        )

    print(
        "Bu kanalda kullanılabilir"
        " SS/CRYPT5 bulunamadı."
    )

    return True, []


def main():

    print("=" * 70)

    print(
        "SADECE SS + HAPP://CRYPT5 VPN TOPLAYICI"
    )

    print("=" * 70)

    names = load_names()

    if not names:

        return

    all_links = []

    successful_channels = 0

    for channel in CHANNELS:

        success, links = process_channel(
            channel
        )

        if success:

            successful_channels += 1

        for link in unique_links(links):

            if link not in all_links:

                all_links.append(link)

    # Tüm kanallar okunamadıysa eski dosyayı koru.

    if successful_channels == 0:

        print(
            "Hiçbir kanal okunamadı."
            " Mevcut çıktı korunuyor."
        )

        return

    # Eski sonuçları silip güncel sonuçları yaz.

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for index, link in enumerate(
            all_links
        ):

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

    print()
    print("=" * 70)

    print(
        "TAMAMLANDI"
    )

    print(
        "Toplam link:",
        len(all_links)
    )

    print(
        "Çıktı:",
        OUTPUT_FILE
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
