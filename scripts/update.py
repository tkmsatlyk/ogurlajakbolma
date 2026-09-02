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
    "https://t.me/s/ares_happ",
    "https://t.me/s/Richman_vpns",
    "https://t.me/s/happvpn",
    "https://t.me/s/expensive_vpn",
    "https://t.me/s/aron58",
]

OUTPUT_FILE = "Toplanan_linkler.txt"
MAX_MESSAGES_TO_SCAN = 100
NAMES_FILE = "names.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    )
}


# ============================================================
# LINK DESENLERİ
# ============================================================

CRYPT5_PATTERN = re.compile(
    r'happ://crypt5/[^\s<>"\']+',
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

HTTPS_PATTERN = re.compile(
    r'https?://[^\s<>"\']+',
    re.IGNORECASE,
)

SS_PATTERN = re.compile(
    r'ss://[^\s<>"\']+',
    re.IGNORECASE,
)


# ============================================================
# LINK TEMİZLE
# ============================================================

def clean_link(link):
    link = html.unescape(link)
    link = link.strip()

    return link.rstrip(
        '.,;:!?)]}\'"<>'
    )


# ============================================================
# HTTP GET
# ============================================================

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
# TARİH PARSE
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

        # ----------------------------------------------------
        # YENİ TELEGRAM MESAJI
        # ----------------------------------------------------

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
                    "text": "",
                    "crypt5": [],
                    "ss": [],
                    "vpn": [],
                    "https": [],
                }

                return

            # Mesaj içerisindeki div
            if self.message_depth > 0:

                self.message_depth += 1

        # ----------------------------------------------------
        # MESAJ ZAMANI
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # ATTRIBUTE İÇERİSİNDE LINK ARA
        # ----------------------------------------------------

        if self.message_depth > 0:

            for value in attrs_dict.values():

                if not value:
                    continue

                self.find_links(value)

    def handle_data(self, data):

        if self.message_depth <= 0:
            return

        self.current_message[
            "text"
        ] += data

        self.find_links(data)

    def find_links(self, text):

        if not self.current_message:
            return

        # ----------------------------------------------------
        # CRYPT5
        # ----------------------------------------------------

        for link in CRYPT5_PATTERN.findall(text):

            link = clean_link(link)

            if link not in self.current_message[
                "crypt5"
            ]:

                self.current_message[
                    "crypt5"
                ].append(link)

        # ----------------------------------------------------
        # SS
        # ----------------------------------------------------

        for link in SS_PATTERN.findall(text):

            link = clean_link(link)

            if link not in self.current_message[
                "ss"
            ]:

                self.current_message[
                    "ss"
                ].append(link)

        for link in VPN_PATTERN.findall(text):
            link = clean_link(link)
            if link not in self.current_message["vpn"]:
                self.current_message["vpn"].append(link)

        for link in HTTPS_PATTERN.findall(text):
            link = clean_link(link)
            if link not in self.current_message["https"]:
                self.current_message["https"].append(link)

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
# KANALIN EN SON MESAJINI BUL
# ============================================================

def get_channel_messages(channel):
    print()
    print("=" * 70)
    print(f"KANAL: {channel}")
    print("=" * 70)
    try:
        content = http_get(channel)
        parser = TelegramMessageParser()
        parser.feed(content)
        if not parser.messages:
            print("Telegram mesajı bulunamadı.")
            return False, []
        dated = []
        for message in parser.messages:
            dt = parse_datetime(message["datetime"])
            if dt is not None:
                dated.append((dt, message))
        if dated:
            dated.sort(key=lambda item: item[0], reverse=True)
            messages = [item[1] for item in dated]
        else:
            messages = list(reversed(parser.messages))
        print(f"Toplam mesaj: {len(messages)}")
        return True, messages
    except Exception as error:
        print(f"Kanal okunamadı: {error}")
        return False, []


# ============================================================
# HAPP / CRYPT5 ÇÖZ
# ============================================================

def decrypt_happ(happ_link):

    print()
    print("-" * 70)
    print(
        "CRYPT5 ÇÖZÜLÜYOR"
    )
    print("-" * 70)

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

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:

            print(
                "hpwnr hata verdi."
            )

            if stderr:
                print(stderr)

            return None

        if not stdout:

            print(
                "hpwnr boş sonuç döndürdü."
            )

            return None

        print(
            "hpwnr çıktısı:"
        )

        print(stdout)

        # ----------------------------------------------------
        # HTTPS BUL
        # ----------------------------------------------------

        match = re.search(
            r'https?://[^\s<>"\']+',
            stdout,
            re.IGNORECASE,
        )

        if match:

            url = clean_link(
                match.group(0)
            )

            print()
            print(
                "ÇÖZÜLEN HTTPS:"
            )
            print(url)

            return url

        # Çıktı zaten direkt HTTPS ise
        if stdout.startswith(
            (
                "http://",
                "https://",
            )
        ):

            return clean_link(stdout)

        print(
            "CRYPT5 sonucunda HTTPS bulunamadı."
        )

        return None

    except FileNotFoundError:

        print(
            "HATA: hpwnr bulunamadı!"
        )

        return None

    except subprocess.TimeoutExpired:

        print(
            "hpwnr zaman aşımına uğradı."
        )

        return None

    except Exception as error:

        print(
            f"CRYPT5 çözme hatası: {error}"
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
            + "=" * (-len(text) % 4),
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
    """
    Çözülen HTTPS aboneliğini alır ve içindeki TÜM VPN linklerini çıkarır.

    Önce hpwnr ile 'uri' dönüşümü denenir. Böylece Xray/JSON/Base64/
    şifreli subscription profilleri doğrudan proxy URI'larına çevrilebilir.
    hpwnr başarısız olursa normal HTTP + Base64 ayrıştırmasına geri düşülür.
    """
    print()
    print("-" * 70)
    print("CRYPT5 SONRASI ABONELİK OKUNUYOR")
    print("-" * 70)
    print(url)

    # ------------------------------------------------------------
    # 1) hpwnr ile FETCH + URI CONVERT
    # ------------------------------------------------------------
    try:
        result = subprocess.run(
            ["hpwnr", url, "uri"],
            capture_output=True,
            text=True,
            timeout=90,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0 and stdout:
            converted_links = VPN_PATTERN.findall(stdout)

            cleaned = []
            for link in converted_links:
                link = clean_link(link)
                if link and link not in cleaned:
                    cleaned.append(link)

            if cleaned:
                print(
                    f"hpwnr ile çıkarılan TÜM VPN linki: "
                    f"{len(cleaned)}"
                )
                return cleaned

            print(
                "hpwnr başarılı fakat stdout içinde VPN URI bulunamadı."
            )

        elif stderr:
            print("hpwnr uri çıktısı:")
            print(stderr)

    except FileNotFoundError:
        print("HATA: hpwnr bulunamadı.")
    except subprocess.TimeoutExpired:
        print("hpwnr uri zaman aşımına uğradı.")
    except Exception as error:
        print(f"hpwnr uri hatası: {error}")

    # ------------------------------------------------------------
    # 2) NORMAL HTTP OKUMA
    # ------------------------------------------------------------
    try:
        content = http_get(url)

        print(
            f"İndirilen veri: "
            f"{len(content)} karakter"
        )

        # Direkt VPN URI'ları
        links = VPN_PATTERN.findall(content)

        cleaned = []
        if success:
            successful_channels += 1

        for link in links:
            link = clean_link(link)
            if link and link not in cleaned:
                cleaned.append(link)

        if cleaned:
            print(
                f"HTTP içinden bulunan TÜM VPN linki: "
                f"{len(cleaned)}"
            )
            return cleaned

        # --------------------------------------------------------
        # 3) BASE64 DENEMESİ
        # --------------------------------------------------------
        decoded = try_base64_decode(content)

        if decoded != content:
            links = VPN_PATTERN.findall(decoded)

            cleaned = []
            for link in links:
                link = clean_link(link)
                if link and link not in cleaned:
                    cleaned.append(link)

            if cleaned:
                print(
                    "Base64 sonrası TÜM VPN linki: "
                    f"{len(cleaned)}"
                )
                return cleaned

        print("Abonelik içinde VPN linki bulunamadı.")
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
# NAMES.TXT
# ============================================================

def load_names():

    print()
    print("=" * 70)
    print(
        "names.txt OKUNUYOR"
    )
    print("=" * 70)

    try:

        with open(
            NAMES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            names = []

            for line in file:

                name = line.strip()

                if name:

                    names.append(name)

        print(
            f"İsim sayısı: {len(names)}"
        )

        return names

    except FileNotFoundError:

        print(
            "HATA: names.txt bulunamadı!"
        )

        return []


# ============================================================
# TEK KANALI İŞLE
# ============================================================

def process_channel(channel):
    success, messages = get_channel_messages(channel)
    if not success:
        return False, []
    limit = min(len(messages), MAX_MESSAGES_TO_SCAN)
    print(f"Yeni -> eski tarama: en fazla {limit} mesaj")
    for i in range(limit):
        message = messages[i]
        print()
        print("-" * 70)
        print(f"{i + 1}. MESAJ KONTROL EDİLİYOR")
        if message.get("datetime"):
            print(f"Zaman: {message['datetime']}")

        # SS öncelikli
        if message.get("ss"):
            links = unique_links(message["ss"])
            if links:
                print(f"SS bulundu: {len(links)}")
                return True, links

        # CRYPT5
        for happ_link in message.get("crypt5", []):
            resolved = decrypt_happ(happ_link)
            if not resolved:
                continue
            if isinstance(resolved, list):
                links = unique_links(resolved)
                if links:
                    return True, links
            else:
                for url in resolved if isinstance(resolved, list) else [resolved]:
                    if isinstance(url, str) and url.startswith(("http://", "https://")):
                        links = get_subscription(clean_link(url))
                        if links:
                            return True, unique_links(links)

        # Direkt VPN URI
        direct = [x for x in unique_links(message.get("vpn", [])) if not x.lower().startswith("ss://")]
        if direct:
            print(f"Doğrudan VPN bulundu: {len(direct)}")
            return True, direct

        # HTTPS subscription
        for url in message.get("https", []):
            url = clean_link(url)
            if url.startswith(("http://", "https://")):
                links = get_subscription(url)
                if links:
                    return True, unique_links(links)

        print("Bu mesajda VPN yok -> bir önceki mesaja geçiliyor.")

    print("Tarama sınırında kullanılabilir VPN bulunamadı.")
    return True, []


# ============================================================
# ANA PROGRAM
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "5 KANAL GERİYE DOĞRU OTOMATİK VPN TOPLAYICI"
    )
    print("=" * 70)

    names = load_names()

    if not names:

        print(
            "names.txt kullanılabilir durumda değil."
        )

        return

    all_links = []
    successful_channels = 0

    # ========================================================
    # 5 KANAL
    # ========================================================

    for channel in CHANNELS:

        success, links = process_channel(
            channel
        )

        for link in links:

            link = clean_link(link)

            if link not in all_links:

                all_links.append(link)

    if successful_channels == 0:
        print("Hiçbir kanal okunamadı. Mevcut çıktı korunuyor.")
        return

    # ========================================================
    # ÇIKTIYI HER ÇALIŞMADA YENİDEN OLUŞTUR
    # ========================================================
    # Böylece eski/stale VPN linkleri dosyada kalmaz.
    # Son mesajlarda hiçbir ilgili link yoksa dosya boşaltılır.
    if not all_links:
        print()
        print("=" * 70)
        print("SON MESAJLARDAN HİÇBİR VPN LINKİ BULUNAMADI.")
        print("Toplanan_linkler.txt boş olarak yeniden yazılacak.")
        print("=" * 70)

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            file.write("")

        return

    # ========================================================
    # NAMES.TXT İLE SIRALI İSİMLENDİR
    # ========================================================

    processed_links = []

    for index, link in enumerate(
        all_links
    ):

        # Eski #etiketi varsa kaldır
        link = link.split(
            "#",
            1,
        )[0]

        if index < len(names):

            name = names[index]

        else:

            name = f"VPN {index + 1}"

        processed_links.append(
            f"{link}#{name}"
        )

    # ========================================================
    # TOPLANAN_LINKLER.TXT
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        for link in processed_links:

            file.write(link)
            file.write("\n")

    # ========================================================
    # SONUÇ
    # ========================================================

    print()
    print("=" * 70)
    print(
        "İŞLEM BAŞARIYLA TAMAMLANDI"
    )
    print("=" * 70)

    print(
        f"Toplam VPN/SS linki: "
        f"{len(processed_links)}"
    )

    print(
        f"names.txt isim sayısı: "
        f"{len(names)}"
    )

    print(
        f"Çıktı: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# ============================================================
# ÇALIŞTIR
# ============================================================

if __name__ == "__main__":
    main()


