import base64
import os
import re
import socket
import time
import urllib.parse
import urllib.request

custom_names = [
    "🔥 Pro-VPN-01",
    "⚡ Pro-VPN-02",
    "🚀 Pro-VPN-03",
    "💎 Pro-VPN-04",
    "🌐 Pro-VPN-05",
    "⚡ Pro-VPN-06",
    "🔥 Pro-VPN-07",
    "🚀 Pro-VPN-08",
    "💎 Pro-VPN-09",
    "🌐 Pro-VPN-10",
]


def fetch_url(url):
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  with urllib.request.urlopen(req, timeout=20) as resp:
    return resp.read().decode("utf-8", errors="ignore")


def ping_node(node_url):
  try:
    parsed = urllib.parse.urlparse(node_url)
    host = parsed.hostname
    port = parsed.port
    if not host or not port:
      return 9999

    start = time.time()
    with socket.create_connection((host, port), timeout=1.5):
      return int((time.time() - start) * 1000)
  except:
    return 9999


def main():
  print("--- 3. Adım: Linkler Çekiliyor, Ping Testi ve Kayıt ---")
  if not os.path.exists("decoded_result.txt"):
    print("Hata: decoded_result.txt bulunamadı!")
    return

  with open("decoded_result.txt", "r", encoding="utf-8") as f:
    decoded_text = f.read().strip()

  target_url = None
  https_matches = re.findall(r"https?://[^\s<>\"']+", decoded_text)
  if https_matches:
    for u in https_matches:
      if (
          "t.me" not in u
          and "github" not in u
          and "googleapis" not in u
          and "localhost" not in u
      ):
        target_url = u
        break

  sub_content = ""
  if target_url:
    print(f"Abonelik URL'sinden içerik çekiliyor: {target_url}")
    try:
      sub_content = fetch_url(target_url)
    except Exception as e:
      print(f"URL çekilemedi: {e}")
  else:
    sub_content = decoded_text

  raw_configs = re.findall(
      r"(?:vless|vmess|ss|trojan)://[^\s<>\"']+", sub_content
  )
  if not raw_configs:
    try:
      decoded_sub = base64.b64decode(sub_content.strip()).decode("utf-8")
      raw_configs = (
          re.findall(
              r"(?:vless|vmess|ss|trojan)://[^\s<>\"']+", decoded_sub
          )
          or []
      )
    except:
      pass

  print(f"Toplam bulunan ham node sayısı: {len(raw_configs)}")
  if not raw_configs:
    print("Hiç node bulunamadı.")
    return

  print("Ping testleri başlatılıyor (< 1500ms)...")
  tested_nodes = []
  for config in raw_configs:
    ping = ping_node(config)
    if ping < 1500:
      tested_nodes.append((ping, config))
      print(f"[PASS] Ping: {ping}ms")

  tested_nodes.sort(key=lambda x: x[0])

  final_links = []
  for index, (ping, config) in enumerate(tested_nodes[:10]):
    clean_config = config.split("#")[0]
    assigned_name = (
        custom_names[index] if index < len(custom_names) else f"Pro-Node-{index + 1}"
    )
    final_links.append(f"{clean_config}#{urllib.parse.quote(assigned_name)}")

  if final_links:
    with open("Toplanan_linkler.txt", "w", encoding="utf-8") as f:
      f.write("\n".join(final_links))
    print(
        f"BAŞARILI: Toplam {len(final_links)} adet optimize node"
        " Toplanan_linkler.txt dosyasına yazıldı."
    )
  else:
    print("1500ms altında uygun node bulunamadı.")


if __name__ == "__main__":
  main()

