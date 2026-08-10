import os

INPUT_FILE = "KODLARY"
num_subs = 5
output_prefix = "sub"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Hata: '{INPUT_FILE}' dosyası bulunamadı!")
        return

    # Linkleri güvenli bir şekilde oku (Karakter hatası almamak için errors='ignore' eklendi)
    try:
        with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
            links = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Dosya okunurken hata oluştu: {e}")
        return

    print(f"Toplam okunan link sayısı: {len(links)}")

    if not links:
        print("Uyarı: Dosya boş veya geçerli link bulunamadı.")
        return

    chunk_size = (len(links) + num_subs - 1) // num_subs

    for i in range(num_subs):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk = links[start_idx:end_idx]

        filename = f"{output_prefix}{i + 1}"
        
        # Mevcut sub dosyasının ilk 8 satırını güvenle oku ve koru
        existing_header_lines = []
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8", errors="ignore") as existing_file:
                    lines = existing_file.readlines()
                    existing_header_lines = [line.rstrip('\r\n') for line in lines[:8]]
            except Exception as e:
                print(f"Uyarı ({filename} okunurken hata): {e}")

        # İlk 8 satır ile yeni linkleri birleştir
        new_content_lines = existing_header_lines + chunk

        # Dosyayı güncelle
        try:
            with open(filename, "w", encoding="utf-8") as out_f:
                out_f.write("\n".join(new_content_lines) + ("\n" if new_content_lines else ""))
            print(f"-> '{filename}' başarıyla güncellendi ({len(chunk)} link eklendi).")
        except Exception as e:
            print(f"Hata ({filename} yazılırken): {e}")

if __name__ == "__main__":
    main()
