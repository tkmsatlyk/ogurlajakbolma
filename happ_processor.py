import os
import re
import requests
from bs4 import BeautifulSoup


def fetch_latest_happ_link(channel_url="https://t.me/s/happvpn"):
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
      return None

    soup = BeautifulSoup(response.text, "html.parser")
    messages = soup.find_all("div", class_="tgme_widget_message_text")

    for message in reversed(messages):
      text = message.get_text()
      match = re.search(r"happ://crypt[^\s<]", text)
      if match:
        found_link = match.group(0)
        print(f"Bulunan şifreli link: {found_link}")
        return found_link
  except Exception as e:
    print(f"Kanal taranırken hata oluştu: {e}")

  return None


def decrypt_happ_content(crypt_link):
  print("Link deşifre ediliyor...")
  # Deşifre edilen ham veriler (Test/Örnek verisi):
  decrypted_text = """
    vless://uuid-1@server1:port?type=tcp#EskiIsim1
    vmess://uuid-2@server2:port?type=ws#EskiIsim2
    trojan://uuid-3@server3:port?type=grpc#EskiIsim3
    ss://method:pass@server4:port#EskiIsim4
    vless://uuid-5@server5:port?type=tcp#EskiIsim5
    vless://uuid-6@server6:port?type=tcp#EskiIsim6
    vmess://uuid-7@server7:port?type=ws#EskiIsim7
    trojan://uuid-8@server8:port?type=grpc#EskiIsim8
    ss://method:pass@server9:port#EskiIsim9
    vless://uuid-10@server10:port?type=tcp#EskiIsim10
    """
  return decrypted_text


def process_and_save_links(
    decrypted_data, output_file="Toplanan_linkler.txt"
):
  # Senin istediğin o harika bayraklı ülke isimleri listesi:
  ulke_isimleri = [
      "🇺🇸 𝗨𝗡𝗜𝗧𝗘𝗗 𝗦𝗧𝗔𝗧𝗘𝗦",
      "🇯🇵 𝗝𝗔𝗣𝗔𝗡",
      "🇰🇷 𝗦𝗢𝗨𝗧𝗛 🇰𝗢𝗥𝗘𝗔",
      "🇦🇪 𝗨𝗡𝗜𝗧𝗘𝗗 🇦𝗥𝗔𝗕 𝗘𝗠𝗜𝗥𝗔𝗧𝗘𝗦",
      "🇨🇭 𝗦𝗪𝗜𝗧𝗭𝗘𝗥𝗟𝗔𝗡𝗗",
      "🇸🇬 𝗦𝗜𝗡𝗚𝗔𝗣𝗢𝗥𝗘",
      "🇮🇸 𝗜𝗖𝗘𝗟𝗔𝗡𝗗",
      "🇨🇦 𝗖𝗔𝗡𝗔𝗗𝗔",
      "🇳🇴 🇳𝗢𝗥𝗪𝗔𝗬",
      "🇸🇪 𝗦𝗪𝗘𝗗𝗘𝗡",
  ]

  lines = decrypted_data.strip().split("\n")
  valid_links = []
  protocol_pattern = re.compile(
      r"^(vless|vmess|trojan|ss|ssr|tuic|hysteria2|socks5)://", re.IGNORECASE
  )

  for line in lines:
    line = line.strip()
    if protocol_pattern.match(line):
      valid_links.append(line)

  # Yukarıdan başlayarak tam olarak ilk 10 tanesini seç
  top_10_links = valid_links[:10]
  processed_links = []

  for index, link in enumerate(top_10_links):
    # Linkin sonundaki eski ismi (# işaretinden sonrasını) tamamen sil
    base_link = link.split("#")[0] if "#" in link else link

    # Listeden sıradaki ülkeyi al ve yeni isim olarak ekle
    secilen_isim = ulke_isimleri[index % len(ulke_isimleri)]
    new_named_link = f"{base_link}#{secilen_isim}"
    processed_links.append(new_named_link)

  # Toplanan_linkler.txt dosyasına alt alta kaydet (Yoksa otomatik oluşturur)
  with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(processed_links) + "\n")

  print(
      f"İşlem Başarılı! {len(processed_links)} adet link '{output_file}'"
      " dosyasına kaydedildi."
  )


if __name__ == "__main__":
  crypt_link = fetch_latest_happ_link("https://t.me/s/happvpn")
  if crypt_link:
    decrypted_content = decrypt_happ_content(crypt_link)
    if decrypted_content:
      process_and_save_links(crypt_content, output_file="Toplanan_linkler.txt")
