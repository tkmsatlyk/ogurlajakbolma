import os
import sys

INPUT_FILE = "KODLARY"
num_subs = 5
output_prefix = "sub"

def main():
    print(f"Kontrol ediliyor... Aranan dosya: {INPUT_FILE}")
    
    if not os.path.exists(INPUT_FILE):
        print(f"HATA: '{INPUT_FILE}' dosyası reponun ana dizininde bulunamadı!")
        sys.exit(1)

    try:
        with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
            links = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"HATA: Dosya okunurken hata oluştu: {e}")
        sys.exit(1)

    print(f"KODLARY dosyasından okunan toplam link sayısı: {len(links)}")

    if not links:
        print("HATA: KODLARY dosyası boş veya içinde geçerli satır yok!")
        sys.exit(1)

    for i in range(num_subs):
        filename = f"{output_prefix}{i + 1}"
        
        # Mevcut sub dosyasının ilk 12 satırını oku ve koru
        existing_header_lines = []
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8", errors="ignore") as existing_file:
                    lines = existing_file.readlines()
                    # İlk 12 satırı koru
                    existing_header_lines = [line.rstrip('\r\n') for line in lines[:12]]
            except Exception as e:
                print(f"Uyarı ({filename} okunurken): {e}")

        # İlk 12 satır ile TÜM linkleri birleştir
        new_content_lines = existing_header_lines + links

        # Dosyayı güncelle
        try:
            with open(filename, "w", encoding="utf-8") as out_f:
                out_f.write("\n".join(new_content_lines) + ("\n" if new_content_lines else ""))
            print(f"-> '{filename}' başarıyla güncellendi. Eklenen link sayısı: {len(links)}")
        except Exception as e:
            print(f"HATA ({filename} yazılırken): {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
