import os
import json
from datetime import datetime, date

CONFIG_FILE = "CONFIG"
STATE_FILE = "state.json"
INPUT_FILE = "KODLARY"

def main():
    print("Müşteri takip ve dinamik sub yönetim sistemi çalışıyor...")
    
    # 1. KODLARY linklerini oku
    links = []
    if os.path.exists(INPUT_FILE):
        try:
            with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
                links = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"KODLARY okuma hatası: {e}")

    # 2. CONFIG oku: [slot] [musteri] [gun] (Örn: sub4 Dayanc 12)
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
            print(f"CONFIG okuma hatası: {e}")

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

    # Temel slotlar
    slots = ["sub1", "sub2", "sub3", "sub4", "sub5"]
    for s in config_entries.keys():
        if s not in slots:
            slots.append(s)

    # 4. Her slotu ve repodaki karşılığını yönet
    for slot in slots:
        target_filename = None
        for f in os.listdir('.'):
            if os.path.isfile(f) and (f == slot or f.startswith(slot + " ") or f.startswith(slot + "_") or f.startswith(slot + "-")):
                target_filename = f
                break
        
        if not target_filename:
            target_filename = slot
            with open(target_filename, "w", encoding="utf-8") as f:
                f.write("")

        existing_header = []
        try:
            with open(target_filename, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                existing_header = [line.rstrip('\r\n') for line in lines[:12]]
        except:
            pass

        if slot in config_entries:
            cfg = config_entries[slot]
            customer = cfg["customer"]
            target_days = cfg["days"]

            sub_state = state_data.get(slot, {})
            if sub_state.get("customer") != customer or sub_state.get("days") != target_days:
                state_data[slot] = {
                    "customer": customer,
                    "days": target_days,
                    "start_date": today_str
                }
                sub_state = state_data[slot]
                print(f"-> {slot} ({target_filename}) için yeni müşteri ({customer}) algılandı. Sayaç sıfırlandı.")

            start_date = datetime.strptime(sub_state["start_date"], "%Y-%m-%d").date()
            elapsed = (date.today() - start_date).days

            if elapsed >= target_days:
                print(f"-> {slot} ({customer}) süresi doldu! Linkler temizlendi.")
                content = existing_header
                any_expired = True
                expired_subs.append(f"{slot}({customer})")
            else:
                print(f"-> {slot} ({customer}) aktif. Kalan gün: {target_days - elapsed}")
                content = existing_header + links
        else:
            content = existing_header
            if slot in state_data:
                del state_data[slot]

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
                f.write("COMMIT_MSG=Sub dosyaları güncellendi [skip ci]\n")

if __name__ == "__main__":
    main()
