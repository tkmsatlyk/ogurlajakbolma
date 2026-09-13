# -*- coding: utf-8 -*-
import os
import json
import base64
import requests
from urllib.parse import quote
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor, as_completed

STATE_FILE = "state.json"
KODLARY_FILE = "KODLARY"
KODLARY_V2_FILE = "KODLARY_V2"
KODLARY_V2_OUTPUT = "KODLARY_V2_SONUC.txt"
TOPLANAN_FILE = "Toplanan_linkler.txt"
CONFIG_FILE = "CONFIG"
KAZANC_FILE = "Kazanc.txt"
GUNLUK_UCRET = 2.77
KAZANC_HARIC_SLOTLAR = ("sub10",)
KAZANC_HARIC_ISIMLER = {"reklam", "kanal", "kendim"}
SIFIRLAMA_ANAHTAR_KELIME = "offline"

PROTOCOL_PREFIXES = ("vless://", "vmess://", "trojan://", "ss://", "hysteria://", "hysteria2://", "tuic://")
VALID_FLAG_LETTERS = ("T", "K", "V")

HEADER_TEMPLATE = """#profile-title: \u200b𝗩𝗼𝗿𝗱𝗿𝘅 \u200b𒀭 𝑉𝐼𝑃
#profile-update-interval: 1
#profile-web-page-url: https://t.me/xylen_111
#support-url: https://t.me/xylen_111
#announce:  📡Kömek gerek bolsa — goldaw elmydama taýyn Ynanýandygyňyz üçin sag boluň! Hil we tizligi saýladyňyz tizlik peselse \u200b⟲ şul şekile basaýmaly✅️【-DAY】
#subscription-userinfo: upload=0; download=0; total=0; expire=0"""

EXPIRED_ANNOUNCE = "#announce: ❤️‍🔥SAGBOLUŇ BIZE GUWANANYŇYZ UCIN TAZEDEN VPN KOD ALJAK BOLSAŇYZ SKITKA EDIP BERYÄRIS🟢"

DEAD_LINK_NAME = "🇫🇲🫡VPN KODYŇ VAGTY DOLDY 🤝"
DEAD_LINK = (
    "vless://00000000-0000-0000-0000-000000000000@0.0.0.0:0"
    "?encryption=none&security=none&type=tcp#" + quote(DEAD_LINK_NAME)
)

HTTP_SESSION = requests.Session()
HTTP_TIMEOUT = 8

def safe_read_lines(path):
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
    found = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(PROTOCOL_PREFIXES):
            found.append(line)
    return found

def fetch_subscription(url):
    try:
        resp = HTTP_SESSION.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        raw_text = resp.text.strip()
    except Exception as e:
        print(f"UYARI: '{url}' adresine bağlanılamadı: {e}")
        return url, []

    direct = extract_protocol_lines(raw_text)
    if direct:
        return url, direct

    try:
        padded = raw_text + "=" * (-len(raw_text) % 4)
        decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
        decoded_links = extract_protocol_lines(decoded)
        if decoded_links:
            return url, decoded_links
        print(f"UYARI: '{url}' base64 çözüldü ama içinde tanınan bir VPN linki bulunamadı.")
        return url, []
    except Exception as e:
        print(f"UYARI: '{url}' ne düz metin ne base64 olarak çözülebildi: {e}")
        return url, []

def load_v2_links():
    if not os.path.exists(KODLARY_V2_FILE):
        print(f"UYARI: '{KODLARY_V2_FILE}' dosyası bulunamadı, V havuzu boş kalacak.")
        return []

    sub_urls = [u.strip() for u in safe_read_lines(KODLARY_V2_FILE) if u.strip()]
    sub_urls = [u for u in sub_urls if u.startswith("http://") or u.startswith("https://")]
    if not sub_urls:
        print(f"UYARI: '{KODLARY_V2_FILE}' boş veya geçerli URL yok, V havuzu boş kalacak.")
        return []

    all_links = []
    with ThreadPoolExecutor(max_workers=min(8, len(sub_urls))) as executor:
        futures = {executor.submit(fetch_subscription, url): url for url in sub_urls}
        for future in as_completed(futures):
            url, links = future.result()
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
    up = token.upper()
    if not up or len(up) > 3:
        return None
    if any(ch not in VALID_FLAG_LETTERS for ch in up):
        return None
    if len(set(up)) != len(up):
        return None
    return up

def parse_definition(parts):
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
        flag = "K"
        try:
            days = int(parts[-1])
        except ValueError:
            return None
        customer = " ".join(parts[1:-1])

    if not customer:
        return None
    return customer, days, flag

def build_active_header(remaining_days):
    filled = HEADER_TEMPLATE.replace("【-DAY】", f"【{remaining_days}-DAY】")
    return filled.split("\n")

def build_expired_header():
    lines = HEADER_TEMPLATE.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("#announce:"):
            new_lines.append(EXPIRED_ANNOUNCE)
        else:
            new_lines.append(line)
    return new_lines

def kazanca_dahil_mi(slot, customer):
    if slot in KAZANC_HARIC_SLOTLAR:
        return False
    if customer.strip().lower() in KAZANC_HARIC_ISIMLER:
        return False
    return True

def sifirlama_istegi_var_mi():
    """Kazanc.txt dosyasında herhangi bir satırda 'offline' yazıyorsa True döner."""
    if not os.path.exists(KAZANC_FILE):
        return False
    for line in safe_read_lines(KAZANC_FILE):
        if line.strip().lower() == SIFIRLAMA_ANAHTAR_KELIME:
            return True
    return False

def update_kazanc(state_data, slot, customer, target_days):
    if not kazanca_dahil_mi(slot, customer):
        return
    signature = f"{slot}|{customer}|{target_days}"
    recorded = state_data.setdefault("_kazanc_kayitli", [])
    if signature in recorded:
        return
    tutar = target_days * GUNLUK_UCRET
    history = state_data.setdefault("_kazanc_gecmisi", [])
    history.append({
        "slot": slot, "customer": customer, "days": target_days,
        "tutar": round(tutar, 2), "tarih": date.today().isoformat()
    })
    recorded.append(signature)
    print(f"-> KAZANÇ: {slot} ({customer}, {target_days} gün) -> +{tutar:.2f} manat eklendi.")

def write_combined_report(state_data, durum_listesi):
    history = state_data.get("_kazanc_gecmisi", [])
    total = sum(entry["tutar"] for entry in history)

    lines = []
    lines.append("=== KAZANÇ GEÇMİŞİ ===")
    for entry in history:
        lines.append(f"{entry['tarih']} | {entry['slot']} - {entry['customer']} - "
                      f"{entry['days']} gün - {entry['tutar']:.2f} manat")
    lines.append("")
    lines.append(f"TOPLAM KAZANÇ: {total:.2f} manat")
    lines.append("")
    lines.append("=== DURUM ===")
    for slot, aktif, kalan_gun, customer in durum_listesi:
        if aktif:
            lines.append(f"{slot} 🟢 {customer} - {kalan_gun} gün kaldı")
        elif customer:
            lines.append(f"{slot} 🔴 {customer}")
        else:
            lines.append(f"{slot} 🔴")

    new_content = "\n".join(lines) + "\n"
    try:
        with open(KAZANC_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"-> {KAZANC_FILE} güncellendi. Toplam kazanç: {total:.2f} manat")
    except Exception as e:
        print(f"Yazma hatası ({KAZANC_FILE}): {e}")

def write_sub_file(target_filename, content):
    new_content = "\n".join(content) + ("\n" if content else "")
    if os.path.exists(target_filename):
        try:
            with open(target_filename, "r", encoding="utf-8") as f:
                if f.read() == new_content:
                    return False
        except Exception:
            pass
    try:
        with open(target_filename, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Yazma hatası ({target_filename}): {e}")
        return False

def main():
    print("CONFIG panelinden okuyan sistem başlatıldı...")

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

    # "offline" yazıldıysa kazancı komple sıfırla
    if sifirlama_istegi_var_mi():
        state_data["_kazanc_gecmisi"] = []
        state_data["_kazanc_kayitli"] = []
        print("-> SIFIRLAMA ALGILANDI: Kazanc.txt içinde 'offline' bulundu. "
              "Kazanç geçmişi tamamen silindi, CONFIG'teki aktif müşterilerden yeniden hesaplanacak.")

    config_info = {}
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
    durum_listesi = []
    degisen_dosya_sayisi = 0

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
            durum_listesi.append((slot, False, 0, None))
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
            durum_listesi.append((slot, False, 0, None))
            continue

        if flag is None:
            flag = "K"

        update_kazanc(state_data, slot, customer, target_days)

        chosen_links = []
        for ch in flag:
            chosen_links.extend(pools.get(ch, []))

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

        if elapsed >= target_days:
            print(f"-> {slot} ({customer}) süresi doldu! Sahte/dead link yazıldı.")
            content = build_expired_header() + [DEAD_LINK]
            any_expired = True
            expired_subs.append(f"{slot}({customer})")
            durum_listesi.append((slot, False, 0, customer))
        else:
            if chosen_links:
                print(f"-> {slot} ({customer}, mod: {flag}) aktif. Kalan gün: {remaining_days}. "
                      f"{len(chosen_links)} link eklendi.")
                content = build_active_header(remaining_days) + chosen_links
                durum_listesi.append((slot, True, remaining_days, customer))
            else:
                print(f"-> {slot} ({customer}) aktif ama havuzda ({flag}) hiç link yok!")
                content = build_active_header(remaining_days)
                durum_listesi.append((slot, False, 0, customer))

        if write_sub_file(target_filename, content):
            degisen_dosya_sayisi += 1

    write_combined_report(state_data, durum_listesi)
    print(f"-> Bu çalıştırmada {degisen_dosya_sayisi} sub dosyası fiilen değişti.")

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
