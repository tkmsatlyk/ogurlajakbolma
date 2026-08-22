import re
import urllib.request


def main():
  print("--- 1. Adım: Telegram'dan Kod Çekiliyor ---")
  try:
    req = urllib.request.Request(
        "https://t.me/s/happvpn", headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
      content = resp.read().decode("utf-8", errors="ignore")
  except Exception as e:
    print(f"Telegram bağlantı hatası: {e}")
    return

  happ_matches = re.findall(r"happ://[^\s<>\"']+", content)
  if not happ_matches:
    print("Hiç happ linki bulunamadı.")
    return

  latest_happ = happ_matches[-1].replace("&amp;", "&").strip()

  # Çekilen kodu köprü dosyasına aktar
  with open("latest_happ.txt", "w", encoding="utf-8") as f:
    f.write(latest_happ)

  print(f"Başarılı: Happ kodu latest_happ.txt dosyasına yazıldı -> {latest_happ[:40]}...")


if __name__ == "__main__":
  main()

