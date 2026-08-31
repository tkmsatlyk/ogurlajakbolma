import os
import json
import re
from datetime import datetime, date

STATE_FILE = "state.json"
INPUT_FILE = "KODLARY"
CONFIG_FILE = "CONFIG"

def safe_read_lines(path):
    """Dosyayı UTF-8 olarak okur. Bozuk karakter varsa SESSİZCE silmez,
    uyarı basar ve o karakteri görünür bir işaretle değiştirir."""
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

def main():
    print("CONFIG panelinden okuyan profesyonel sayaç sistemi başlatıldı...")

    # 1. KODLARY link deposunu oku
    links = []
    if os.path.exists(INPUT_FILE):
        for line in safe_read_lines(INPUT_FILE):
            line = line.strip()
            if line:
                links.append(line)

    # 2. State (hafıza) verisini oku
    state_data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state_data = json.load(f)
        except:
            state_data = {}

    # 3. CONFIG dosyasını oku -> "panel" burası.
    config_info = {}  # { "sub3": (customer, days), ... }
    if os.path.exists(CONFIG_FILE):
        for raw_line in safe_read_lines(CONFIG_FILE):
            line = raw_line.strip()
            if not line:
                continue
            parts = line.replace('_', ' ').replace('-', ' ').split()
            if len(parts) < 3:
                continue
            slot_name = parts[0]
            try:
                c_days = int(parts[-1])
            except ValueError:
                print(f"UYARI: CONFIG satırı çözümlenemedi: '{line}'")
                continue
            c_customer = " ".join(parts[1:-1])
            if not c_customer:
                continue
            config_info[slot_name] = (c_customer, c_days)

    today_str = date.today().isoformat()
    any_expired = False
    expired_subs = []

    slots = ["sub1", "sub2", "sub3", "sub4", "sub5", "sub6", "sub7", "sub8", "sub9", "sub10"]

    for slot in slots:
        customer = None
        target_days = None
        source = None

        if slot in config_info:
            customer, target_days = config_info[slot]
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

        file_customer, file_days = None, None
        fname_parts = target_filename.replace('_', ' ').replace('-', ' ').split()
        if len(fname_parts) >= 3:
            try:
                file_days = int(fname_parts[-1])
                file_customer = " ".join(fname_parts[1:-1])
            except ValueError:
                file_customer, file_days = None, None

        if customer is None or target_days is None:
            customer, target_days = file_customer, file_days
            source = "dosya adı"
        elif file_customer and file_days is not None:
            if file_customer != customer or file_days != target_days:
                print(f"UYARI: {slot} için CONFIG ('{customer} {target_days}') ile dosya adı "
                      f"('{file_customer} {file_days}') FARKLI! CONFIG değeri kullanılacak.")

        if not customer or target_days is None:
            print(f"-> {slot} boş (CONFIG'te ve dosya adında müşteri bilgisi yok), atlanıyor.")
            continue

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
            print(f"-> {slot} ({customer}, kaynak: {source}) için yeni kayıt algılandı. Sayaç sıfırlandı.")

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
            print(f"-> {slot} ({customer}) aktif. Kalan gün: {remaining_days}")
            content = updated_header + links

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
