import base64
import os
import re
import requests
from bs4 import BeautifulSoup
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.serialization import load_pem_private_key


def decrypt_happ_with_rsa(crypt_link):
  """LeeeeT/happ-decryptor reposundaki RSA mantığıyla happ://crypt kodunu

  gerçekten çözer.
  Repoda 'private.pem' veya 'key.pem' adında RSA private key dosyası olmalıdır.
  """
  if not crypt_link.startswith("happ://"):
    return crypt_link

  try:
    # Linkin payload kısmını al
    parts = crypt_link.split("://")
    if len(parts) < 2:
      return crypt_link

    sub_part = parts[1]
    payload = sub_part.split("/", 1)[1] if "/" in sub_part else sub_part

    # Base64 URL-safe decode
    padding_needed = len(payload) % 4
    if padding_needed:
      payload += "=" * (4 - padding_needed)
    encrypted_bytes = base64.urlsafe_b64decode(payload)

    # Repo içindeki RSA Private Key dosyasını ara
    key_files = ["private.pem", "key.pem", "rsa_private.pem", "private_key.pem"]
    private_key_obj = None

    for kf in key_files:
      if os.path.exists(kf):
        with open(kf, "rb") as key_file:
          private_key_obj = load_pem_private_key(key_file.read(), password=None)
        break

    if private_key_obj:
      # RSA PKCS1v15 veya OAEP (happ-decryptor reposunda hangisi kullanılıyorsa) ile çöz
      try:
        decrypted_bytes = private_key_obj.decrypt(
            encrypted_bytes,
            padding.PKCS1v15(),  # veya OAEP gerekiyorsa burası güncellenir
        )
        res_text = decrypted_bytes.decode("utf-8", errors="ignore")
        match = re.search(r"https?://[^\s<>'\"]+", res_text)
        if match:
          return match.group(0)
      except Exception as rsa_err:
        print(f"RSA deşifreleme hatası: {rsa_err}")

    # Eğer key dosyası yoksa ya da doğrudan çözülebildiyse düz metin/base64 dönüşü dener
    return decoded_bytes.decode("utf-8", errors="ignore")

  except Exception as e:
    print(f"Happ link çözme genel hata: {e}")
    return crypt_link


def update_links():
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
      print(f"Kanala erişilemedi. Kod: {response.status_code}")
      return

    soup = BeautifulSoup(response.text, "html.parser")
    messages = soup.find_all("div", class_="tgme_widget_message_text")

    all_found_links = []
    for message in reversed(messages):
      text = message.get_text()
      urls = re.findall(
          r"(happ://[^\s<>'\"]+|https?://[^\s<>'\"]+|vless://[^\s<>'\"]+|vmess://[^\s<>'\"]+|trojan://[^\s<>'\"]+|ss://[^\s<>'\"]+)",
          text,
      )
      for u in urls:
        if u not in all_found_links:
          all_found_links.append(u)

    raw_proxy_lines = []

    for item in all_found_links:
      # happ://crypt kodunu RSA ile kır ve https aboneliğini al
      if item.startswith("happ://"):
        resolved_url = decrypt_happ_with_rsa(item)
        print(f"Çözülen link: {item} -> {resolved_url}")
        item = resolved_url

      # Elde edilen https:// aboneliğinin içine gir
      if item.startswith("http://") or item.startswith("https://"):
        try:
          sub_res = requests.get(item, headers=headers, timeout=10)
          if sub_res.status_code == 200:
            content = sub_res.text
            try:
              decoded_sub = base64.b64decode(content.strip())
              content = decoded_sub.decode("utf-8", errors="ignore")
            except Exception:
              pass

            for line in content.splitlines():
              line = line.strip()
              if line and "://" in line:
                raw_proxy_lines.append(line)
        except Exception as e:
          print(f"Abonelik dosyası indirilemedi: {e}")

      elif any(
          item.startswith(p)
          for p in ["vless://", "vmess://", "trojan://", "ss://", "ssr://"]
      ):
        raw_proxy_lines.append(item)

    protocol_pattern = re.compile(
        r"^(vless|vmess|trojan|ss|ssr|tuic|hysteria2|socks5)://", re.IGNORECASE
    )
    valid_links = [
        line for line in raw_proxy_lines if protocol_pattern.match(line)
    ]

    # Yukarıdan aşağıya tam 10 tane seç
    top_10_links = valid_links[:10]

    if not top_10_links:
      print("Hiç geçerli link bulunamadı!")
      return

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
        "🇸🇪 🇸𝗪𝗘𝗗𝗘𝗡",
    ]

    processed_links = []
    for index, link in enumerate(top_10_links):
      base_link = link.split("#")[0] if "#" in link else link
      secilen_isim = ulke_isimleri[index % len(ulke_isimleri)]
      processed_links.append(f"{base_link}#{secilen_isim}")

    with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
      f.write("\n".join(processed_links) + "\n")

    print(
        "İşlem tamam! Toplanan_linkler.txt dosyasına 10 adet link aktarıldı."
    )

  except Exception as e:
    print(f"Hata oluştu: {e}")


if __name__ == "__main__":
  update_links()
