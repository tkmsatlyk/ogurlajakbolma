import os
import json
import re
from datetime import datetime, date

CONFIG_FILE = "CONFIG"
STATE_FILE = "state.json"
INPUT_FILE = "KODLARY"

def main():
    print("Sistem kontrolü başlatıldı...")
    
    # 1. KODLARY (Link deposu) oku
    links = []
    if os.path.exists(INPUT_FILE):
        try:
            with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
                links = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Link dosyası okunamadı: {e}")

    # 2. CONFIG oku: [slot] [musteri] [gun]
    config_entries = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        slot = parts[0]
                        customer = parts[1]
                        try:
                            days = int(parts[2])
                            config_entries[slot] = {"customer": customer, "days": days}
                        except ValueError:
                            pass
        except Exception as e:
            print(f"CONFIG dosyası okunamadı: {e}")

    # 3. State verisini oku
    state_data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state_data = json.load(f)
        except:
            state_data = {}

    today_str = date.today().isoformat()
    any_expired = False
    expired_subs = []

    # Yönetilecek slotlar
    all_slots = ["sub1", "sub2", "sub3", "sub4", "sub5"]
    for s in config_entries.keys():
        if s not in all_slots:
            all_slots.append(s)

    # 4. Her slotu işle
    for slot in all_slots:
        target_filename = None
        for f in os.listdir('.'):
            if os.path.isfile(f) and (f == slot or f.startswith(slot + " ") or f.startswith(slot + "_") or f.startswith(slot + "-")):
                target_filename = f
                break
        
        # Dosya yoksa pas geç
        if not target_filename:
            continue

        # Dosyanın içini oku, sadece ilk 12 satırı header (başlık) olarak al
        lines = []
        try:
            with open(target_filename, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except:
            lines = []
        
        existing_header = [line.rstrip('\r\n') for line in lines[:12]]

        if slot in config_entries:
            cfg = config_entries[slot]
            customer = cfg["customer"]
            target_days = cfg["days"]

            sub_state = state_data.get(slot, {})
            # Yeni müşteri geldiğinde süreyi sıfırla
            if sub_state.get("customer") != customer or sub_state.get("days") != target_days:
                state_data[slot] = {
                    "customer": customer,
                    "days": target_days,
                    "start_date": today_str
                }
                sub_state = state_data[slot]
                print(f"-> {slot} ({customer}) için yeni kayıt oluşturuldu.")

            start_date = datetime.strptime(sub_state["start_date"], "%Y-%m-%d").date()
            elapsed = (date.today() - start_date).days
            remaining_days = max(target_days - elapsed, 0)

            # Anons (header) içerisindeki gün sayısını [X-DAY] formatında güncelle
            updated_header = []
            for line in existing_header:
                if "-DAY" in line.upper() or "-GÜN" in line.upper():
                    # Köşeli parantez içindeki sayıyı güncelle
                    new_line = re.sub(r'\[(\d+)(-DAY|-G[uü]N)\]', f'[{remaining_days}\\2]', line, flags=re.IGNORECASE)
                    updated_header.append(new_line)
                else:
                    updated_header.append(line)

            # Link yönetimi: Süre dolduysa sadece 12 satırı yaz, dolmadıysa linkleri ekle
            if elapsed >= target_days:
                print(f"-> {slot} süresi doldu. Linkler temizlendi.")
                content = updated_header
                any_expired = True
                expired_subs.append(f"{slot}({customer})")
            else:
                print(f"-> {slot} ({customer}) aktif. Kalan gün: {remaining_days}")
                content = updated_header + links
        else:
            # Config'de olmayan dosyayı olduğu gibi bırak (linklere dokunma)
            content = existing_header + lines[12:]
            if slot in state_data:
                del state_data[slot]

        # Dosyayı güncelle
        try:
            with open(target_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(content) + ("\n" if content else ""))
        except Exception as e:
            print(f"Yazma hatası ({target_filename}): {e}")

    # State dosyasını kaydet
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"State kaydedilemedi: {e}")

    # GitHub Action Commit mesajı
    github_env = os.getenv("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as f:
            if any_expired:
                f.write(f"COMMIT_MSG=Süresi dolanlar temizlendi: {', '.join(expired_subs)}\n")
            else:
                f.write("COMMIT_MSG=Anons gun sayaci otomatik guncellendi [skip ci]\n")

if __name__ == "__main__":
    main()
