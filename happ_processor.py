import os
import re
import requests
from bs4 import BeautifulSoup

# --- 1. ADIM: KANALDAKİ HAPPN LİNKİNİ ÇEK VE toplanan_linkler.txt'Yİ GÜNCELLE ---


def update_toplanan_linkler():
  channel_url = "https://t.me/s/happvpn"
  print(f"Kanal taranıyor: {channel_url}")
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  try:
    response = requests.get(channel_url, headers=headers, timeout=15)
    if response.status_code != 200:
      print(f"Kanal sayfasına erişilemedi. Kod: {response.status_code}")
      return False

    soup = BeautifulSoup(response.text, "html.parser")
    messages = soup.find_all("div", class_="tgme_widget_message_text")

    crypt_link = None
    for message in reversed(messages):
      text = message.get_text()
      match = re.search(r"happ://crypt[^\s<]", text)
      if match:
        crypt_link = match.group(0)
        break

    if not crypt_link:
      print("Kanalda crypt linki bulunamadı.")
      return False

    print(f"Bulunan şifreli link: {crypt_link}")

    # Not: Deşifreleme aşaması (Gerçek ortamda çözülmüş ham metin buraya gelecek)
    decrypted_text = """
        vless://uuid-1@server1:port?type=tcp#Old1
        vmess://uuid-2@server2:port?type=ws#Old2
        trojan://uuid-3@server3:port?type=grpc#Old3
        ss://method:pass@server4:port#Old4
        vless://uuid-5@server5:port?type=tcp#Old5
        vless://uuid-6@server6:port?type=tcp#Old6
        vmess://uuid-7@server7:port?type=ws#Old7
        trojan://uuid-8@server8:port?type=grpc#Old8
        ss://method:pass@server9:port#Old9
        vless://uuid-10@server10:port?type=tcp#Old10
        """

    # İstediğin bayraklı ülke isimleri listesi
    ulke_isimleri = [
        "🇺🇸 𝗨𝗡𝗜𝗧𝗘𝗗 𝗦𝗧𝗔𝗧𝗘𝗦",
        "🇯🇵 🇯𝗔𝗣𝗔𝗡",
        "🇰🇷 𝗦𝗢𝗨𝗧𝗛 🇰𝗢𝗥𝗘𝗔",
        "🇦🇪 𝗨𝗡𝗜𝗧𝗘𝗗 🇦𝗥𝗔𝗕 𝗘𝗠𝗜𝗥𝗔𝗧𝗘𝗦",
        "🇨🇭 𝗦𝗪𝗜𝗧𝗭𝗘𝗥𝗟𝗔𝗡𝗗",
        "🇸🇬 🇸𝗜𝗡𝗚𝗔𝗣𝗢𝗥𝗘",
        "🇮🇸 𝗜𝗖𝗘𝗟𝗔𝗡𝗗",
        "🇨🇦 𝗖𝗔𝗡𝗔𝗗𝗔",
        "🇳🇴 🇳𝗢𝗥𝗪𝗔𝗬",
        "🇸🇪 𝗦𝗪𝗘𝗗𝗘𝗡",
    ]

    lines = decrypted_text.strip().split("\n")
    valid_links = []
    protocol_pattern = re.compile(
        r"^(vless|vmess|trojan|ss|ssr|tuic|hysteria2|socks5)://", re.IGNORECASE
    )

    for line in lines:
      line = line.strip()
      if protocol_pattern.match(line):
        valid_links.append(line)

    top_10_links = valid_links[:10]
    processed_links = []

    for index, link in enumerate(top_10_links):
      base_link = link.split("#")[0] if "#" in link else link
      secilen_isim = ulke_isimleri[index % len(ulke_isimleri)]
      processed_links.append(f"{base_link}#{secilen_isim}")

    # Kesinlikle küçük harfle toplanan_linkler.txt olarak kaydediliyor
    with open("toplanan_linkler.txt", "w", encoding="utf-8") as f:
      f.write("\n".join(processed_links) + "\n")

    print("toplanan_linkler.txt başarıyla güncellendi!")
    return True

  except Exception as e:
    print(f"Hata oluştu: {e}")
    return False


# --- 2. ADIM: DOSYA İSİMLERİNDEKİ GÜNLERİ DÜŞÜR VE SUB DOSYALARINI GÜNCELLE ---


def update_sub_files():
  if not os.path.exists("toplanan_linkler.txt"):
    print("toplanan_linkler.txt bulunamadı, önce linkler çekilmeli.")
    return

  with open("toplanan_linkler.txt", "r", encoding="utf-8") as f:
    toplanan_linkler_content = f.read().strip()

  # Repodaki dosyaları tara (Örn: sub1 rahmanguly 12)
  pattern = re.compile(r"^(sub\d+)\s+(.+)\s+(\d+)$")

  for filename in os.listdir("."):
    match = pattern.match(filename)
    if match:
      prefix = match.group(1)  # sub1
      name = match.group(2)  # rahmanguly
      days = int(match.group(3))  # 12

      # Günü 1 azalt
      new_days = max(0, days - 1)
      new_filename = f"{prefix} {name} {new_days}"

      # Dosyanın içeriğini oku (İlk 12 satırı korumak için)
      target_lines = []
      if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as tf:
          target_lines = tf.readlines()

      header_lines = target_lines[:12] if len(target_lines) >= 12 else target_lines

      # İlk 12 satırdaki sayaç kalıbını güncelle
      new_header_lines = []
      for h_line in header_lines:
        if "-DAY" in h_line:
          h_line = re.sub(r"【\d*-?DAY】", f"【{new_days}-DAY】", h_line)
        new_header_lines.append(h_line)

      # İçeriği birleştir: İlk 12 satır + boşluk + toplanan_linkler.txt içeriği
      new_content = "".join(new_header_lines)
      if not new_content.endswith("\n"):
        new_content += "\n"
      new_content += "\n" + toplanan_linkler_content + "\n"

      if filename != new_filename:
        os.remove(filename)

      with open(new_filename, "w", encoding="utf-8") as tf:
        tf.write(new_content)

      print(
          f"Güncellendi: {filename} -> {new_filename} (Kalan gün: {new_days})"
      )


if __name__ == "__main__":
  print("Otomasyon başlatıldı...")
  success = update_toplanan_linkler()
  if success:
    update_sub_files()
  print("Tüm işlemler bitti!")
