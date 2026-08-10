import os

# Dosya adı: KODLARY
INPUT_FILE = "KODLARY"

# İstediğin güncel profil başlığı (Asla silinmeyecek)
HEADER_TEXT = """#providerid: ​𓅓 VØRÐR™︎ˢᵉʳᵛⁱᶜᵉ 🔱​
#profile-title: ​𓅓 VØRÐR™︎ˢᵉʳᵛⁱᶜᵉ 🔱​
#profile-update-interval: 0
#profile-web-page-url: https://t.me/xylen_111
#support-url: https://t.me/xylen_111
#announce: 🦾𝑲𝑶𝑫 𝑰𝑺𝑳𝑬𝑴𝑬𝑺𝑬 𝟏 𝟐 𝑴𝑰𝑵𝑼𝑻📲𝑮𝑨𝑹𝑨𝑺𝒀𝑷 𝑶𝑩𝑵𝑨𝑽𝑰𝑻 𝑬𝑫𝑰Ň✅️
#subscription-userinfo: upload=0; download=0; total=0; expire=0"""

def update_sub_files(input_file=INPUT_FILE, num_subs=5, output_prefix="sub"):
    if not os.path.exists(input_file):
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        return

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
        file_content = HEADER_TEXT + "\n" + ("\n".join(chunk) + "\n" if chunk else "")

        with open(filename, "w", encoding="utf-8") as out_f:
            out_f.write(file_content)

        print(f"-> '{filename}' güncellendi.")

if __name__ == "__main__":
    update_sub_files()
