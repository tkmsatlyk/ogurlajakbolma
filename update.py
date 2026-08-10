import os

# Dosya adı: KODLARY
INPUT_FILE = "KODLARY"

def update_sub_files(input_file=INPUT_FILE, num_subs=5, output_prefix="sub"):
    if not os.path.exists(input_file):
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        return

    # Ana dosyadaki linkleri oku
    with open(input_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        print("Uyarı: Dosya boş.")
        return

    chunk_size = (len(links) + num_subs - 1) // num_subs

    for i in range(num_subs):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk = links[start_idx:end_idx]

        filename = f"{output_prefix}{i + 1}"
        
        # Mevcut sub dosyasının ilk 8 satırını oku ve koru
        existing_header_lines = []
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as existing_file:
                lines = existing_file.readlines()
                # İlk 8 satırı al (varsa)
                existing_header_lines = [line.rstrip('\r\n') for line in lines[:8]]

        # İlk 8 satır ile yeni linkleri birleştir
        new_content_lines = existing_header_lines + chunk

        # Dosyaya yaz
        with open(filename, "w", encoding="utf-8") as out_f:
            out_f.write("\n".join(new_content_lines) + ("\n" if new_content_lines else ""))

        print(f"-> '{filename}' güncellendi: İlk 8 satıra dokunulmadı, altındaki linkler yenilendi.")

if __name__ == "__main__":
    update_sub_files()
