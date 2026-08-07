import os

# Sabit profil başlığı (Asla silinmeyecek)
HEADER_TEXT = """#providerid: ​𓅓 VØRÐR™︎ˢᵉʳᵛⁱᶜᵉ 🔱​
#profile-title: ​𓅓 VØRÐR™︎ˢᵉʳᵛⁱᶜᵉ 🔱​
#profile-update-interval: 0
#profile-web-page-url: https://lssjsiwjsjzk
#support-url: https://lssjsiwjsjzk
#announce: VPN İŞLEMESE📱BIR AZ GARAŞYP📲OBNAVİT EDIP GORUŇ🦾 
#subscription-userinfo: upload=0; download=0; total=0;"""

def update_sub_files(input_file="toplanan_linkler.txt", num_subs=5, output_prefix="sub"):
    # Kaynak dosya kontrolü
    if not os.path.exists(input_file):
        print(f"Hata: '{input_file}' dosyası bulunamadı!")
        return

    # Linkleri oku ve boş satırları temizle
    with open(input_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        print("Uyarı: Kaynak dosya boş.")
        return

    # Linkleri sub dosyalarına eşit şekilde paylaştır
    chunk_size = (len(links) + num_subs - 1) // num_subs

    for i in range(num_subs):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk = links[start_idx:end_idx]

        # Uzantısız dosya adı (sub1, sub2, sub3, sub4, sub5)
        filename = f"{output_prefix}{i + 1}"

        # Eski linkleri sil, başlığı koru ve yeni linkleri yaz
        file_content = HEADER_TEXT + "\n" + ("\n".join(chunk) + "\n" if chunk else "")

        with open(filename, "w", encoding="utf-8") as out_f:
            out_f.write(file_content)

        print(f"-> '{filename}' dosyası güncellendi: Eski linkler silindi, başlık korundu ve {len(chunk)} bağlantı eklendi.")

if __name__ == "__main__":
    update_sub_files("toplanan_linkler.txt", num_subs=5)
