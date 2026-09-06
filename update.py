import os
import json
import re
import base64
import requests
from datetime import datetime, date

STATE_FILE = "state.json"
KODLARY_FILE = "KODLARY"
KODLARY_V2_FILE = "KODLARY_V2"
KODLARY_V2_OUTPUT = "KODLARY_V2_SONUC.txt"
TOPLANAN_FILE = "Toplanan_linkler.txt"
CONFIG_FILE = "CONFIG"

PROTOCOL_PREFIXES = ("vless://", "vmess://", "trojan://", "ss://", "hysteria://", "hysteria2://", "tuic://")
VALID_FLAG_LETTERS = ("T", "K", "V")

def safe_read_lines(path):
    """Dosyayı UTF-8 olarak okur. Bozuk karakter varsa uyarı basar, sessizce silmez."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            print(f"UYARI: '{path}' dosyasında bozuk karakter bulundu ({e}). "
                  f"Karakter(ler) '?' ile değiştirilecek, dosyayı kontrol et.")
            text = raw.decode("utf-8", errors="replace")
        return text.splitlines(keepends=True)
    except Exception as e:
        print(f"Okuma hatası ({path}): {e}")
        return []

def load_links(path):
    links = []
    if os.path.exists(path):
        for line in safe_read_lines(path):
            line = line.strip()
            if line:
                links.append(line)
    else:
        print(f"UYARI: '{path}' dosyası bulunamadı, boş kabul edilecek.")
    return links

def extract_protocol_lines(text):
    """Sadece vless/vmess/trojan/ss/hysteria/tuic ile başlayan satırları alır,
    #profile-title, #announce gibi başlık satırlarını hiç almaz."""
    found = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(PROTOCOL_PREFIXES):
            found.append(line)
    return found

def fetch_subscription(url):
    """Bir subscription URL'sine gidip içindeki linkleri döndürür.
    Önce düz metin arar, olmazsa base64 çözmeyi dener."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        raw_text = resp.text.strip()
    except Exception as e:
        print(f"UYARI: '{url}' adresine bağlanılamadı: {e}")
        return []

    direct = extract_protocol_lines(raw_text)
    if direct:
        return direct

    try:
        padded = raw_text + "=" * (-len(raw_text) % 4)
        decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
        decoded_links = extract_protocol_lines(decoded)
        if decoded_links:
            return decoded_links
        print(f"UYARI: '{url}' base64 çözüldü ama içinde tanınan bir VPN linki bulunamadı.")
        return []
    except Exception as e:
        print(f"UYARI: '{url}' ne düz metin ne base64 olarak çözülebildi: {e}")
        return []

def load_v2_links():
    """KODLARY_V2'deki subscription URL'lerini çekip kendi ayrı havuzunu döndürür.
    KODLARY dosyasına HİÇ dokunmaz, sadece bilgi amaçlı KODLARY_V2_SONUC.txt'ye yazar."""
    if not os.path.exists(KODLARY_V2_FILE):
        print(f"UYARI: '{KODLARY_V2_FILE}' dosyası bulunamadı, V havuzu boş kalacak.")
        return []

    sub_urls = [u.strip() for u in safe_read_lines(KODLARY_V2_FILE) if u.strip()]
    if not sub_urls:
        print(f"UYARI: '{KODLARY_V2_FILE}' boş, V havuzu boş kalacak.")
        return []

    all_links = []
    for url in sub_urls:
        if not url.startswith("http://") and not url.startswith("https://"):
            print(f"UYARI: '{url}' bir HTTP/HTTPS linki gibi görünmüyor, atlanıyor.")
            continue
        links = fetch_subscription(url)
        print(f"-> (V havuzu) '{url}' üzerinden {len(links)} link çekildi.")
        all_links.extend(links)

    if all_links:
        try:
            with open(KODLARY_V2_OUTPUT, "w", encoding="utf-8") as f:
                f.write("\n".join(all_links) + "\n")
        except Exception as e:
            print(f"Yazma hatası ({KODLARY_V2_OUTPUT}): {e}")
    else:
        print("UYARI: KODLARY_V2'deki hiçbir subscription'dan link çekilemedi. V havuzu boş.")

    return all_links

def parse_flag(token):
    """T, K, V harflerinden oluşan, her harf en fazla 1 kere geçen bir kombinasyon.
    Örnek geçerli: T, K, V, TK, KT, TV, VT, KV, VK, TKV, VKT, ..."""
    up = token.upper()
    if not up or len(up) > 3:
        return None
    if any(ch not in VALID_FLAG_LETTERS for ch in up):
        return None
    if len(set(up)) != len(up):  # aynı harf tekrar etmesin
        return None
    return up

def parse_definition(parts):
    """parts[0] slot adı; geri kalanı customer + days (+ opsiyonel T/K/V kombinasyonu).
    Dönüş: (customer, days, flag) veya None"""
    if len(parts) < 3:
        return None

    flag = parse_flag(parts[-1])
    if flag:
        if len(parts) < 4:
            return None
        try:
            days = int(parts[-2])
        except ValueError:
            return None
        customer = " ".join(parts[1:-2])
    else:
        flag = "K"  # harf yoksa eski satırlarla uyumlu -> varsayılan KODLARY
        try:
            days = int(parts[-1])
        except ValueError:
            return None
        customer = " ".join(parts[1:-1])

    if not customer:
        return None
    return customer, days, flag

def main():
    print("CONFIG panelinden okuyan (T/K/V destekli) sayaç sistemi başlatıldı...")

    kodlary_links = load_links(KODLARY_FILE)
    toplanan_links = load_links(TOPLANAN_FILE)
    v2_links = load_v2_links()

    pools = {"T": toplanan_links, "K": kodlary_links, "V": v2_links}

    state_data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state_data = json.load(f)
        except:
            state_data = {}

    config_info = {}  # { "sub3": (customer, days, flag), ... }
    if os.path.exists(CONFIG_FILE):
        for raw_line in safe_read_lines(CONFIG_FILE):
            line = raw_line.strip()
            if not line:
                continue
            parts = line.replace('_', ' ').replace('-', ' ').split()
            parsed = parse_definition(parts)
            if parsed is None:
                if len(parts) >= 3:
                    print(f"UYARI: CONFIG satırı çözümlenemedi: '{line}'")
                continue
            slot_name = parts[0]
            config_info[slot_name] = parsed

    today_str = date.today().isoformat()
    any_expired = False
    expired_subs = []

    slots = ["sub1", "sub2", "sub3", "sub4", "sub5",
              "sub6", "sub7", "sub8", "sub9", "sub10"]

    for slot in slots:
        customer = None
        target_days = None
        flag = None
        source = None

        if slot in config_info:
            customer, target_days, flag = config_info[slot]
            source = "CONFIG"

        matches = sorted(
            f for f in os.listdir('.')
            if os.path.isfile(f) and (
                f == slot or f.startswith(slot + " ") or
                f.startswith(slot + "_") or f.startswith(slot + "-")
            )
        )
        if len(matches) > 1:
            print(f"UYARI: {slot} için birden fazla dosya bulundu: {matches}. "
                  f"'{matches[0]}' kullanılacak, diğerlerini silmeyi düşün.")
        if not matches:
            print(f"-> {slot} için hiç dosya bulunamadı, atlanıyor.")
            continue

        target_filename = matches[0]

        fname_parts = target_filename.replace('_', ' ').replace('-', ' ').split()
        file_parsed = parse_definition(fname_parts)

        if customer is None or target_days is None:
            if file_parsed:
                customer, target_days, flag = file_parsed
                source = "dosya adı"
        elif file_parsed:
            f_customer, f_days, f_flag = file_parsed
            if f_customer != customer or f_days != target_days:
                print(f"UYARI: {slot} için CONFIG ('{customer} {target_days} {flag}') ile "
                      f"dosya adı ('{f_customer} {f_days} {f_flag}') FARKLI! CONFIG değeri kullanılacak.")

        if not customer or target_days is None:
            print(f"-> {slot} boş (CONFIG'te ve dosya adında müşteri bilgisi yok), atlanıyor.")
            continue

        if flag is None:
            flag = "K"

        # Harflerin yazıldığı sırayla havuzları birleştir (örn. "KV" -> önce K sonra V)
        chosen_links = []
        for ch in flag:
            chosen_links.extend(pools.get(ch, []))

        lines = safe_read_lines(target_filename)
        existing_header = [line.rstrip('\r\n') for line in lines[:12]]

        sub_state = state_data.get(slot, {})
        if sub_state.get("customer") != customer or sub_state.get("days") != target_days:
            state_data[slot] = {
                "customer": customer,
                "days": target_days,
                "start_date": today_str
            }
            sub_state = state_data[slot]
            print(f"-> {slot} ({customer}, kaynak: {source}, mod: {flag}) için yeni kayıt algılandı. Sayaç sıfırlandı.")

        start_date = datetime.strptime(sub_state["start_date"], "%Y-%m-%d").date()
        elapsed = (date.today() - start_date).days
        remaining_days = max(target_days - elapsed, 0)

        updated_header = []
        for line in existing_header:
            if "-DAY" in line.upper() or "-GÜN" in line.upper() or "-GUN" in line.upper():
                new_line = re.sub(
                    r'[\[【](\d+)(-DAY|-G[UÜ]N)[\]】]',
                    lambda m: f'【{remaining_days}{m.group(2)}】',
                    line,
                    flags=re.IGNORECASE
                )
                updated_header.append(new_line)
            else:
                updated_header.append(line)

        if elapsed >= target_days:
            print(f"-> {slot} ({customer}) süresi doldu! Linkler temizlendi.")
            content = updated_header
            any_expired = True
            expired_subs.append(f"{slot}({customer})")
        else:
            print(f"-> {slot} ({customer}, mod: {flag}) aktif. Kalan gün: {remaining_days}. "
                  f"{len(chosen_links)} link eklendi.")
            content = updated_header + chosen_links

        try:
            with open(target_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(content) + ("\n" if content else ""))
        except Exception as e:
            print(f"Yazma hatası ({target_filename}): {e}")

    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"State kaydedilemedi: {e}")

    github_env = os.getenv("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as f:
            if any_expired:
                f.write(f"COMMIT_MSG=Süresi dolanlar temizlendi: {', '.join(expired_subs)}\n")
            else:
                f.write("COMMIT_MSG=Anons gun sayaci otomatik guncellendi [skip ci]\n")

if __name__ == "__main__":
    main()
