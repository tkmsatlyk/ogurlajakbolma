import os
import re
import socket
import subprocess
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
  print("--- Decryptor Reposu Kontrol Ediliyor ---")
  if not os.path.exists("happ-decryptor"):
    subprocess.run(
        [
            "git",
            "clone",
            "https://github.com/LeeeeT/happ-decryptor.git",
            "happ-decryptor",
        ],
        check=True,
    )

  print("--- Telegram Kanalı Taranıyor ---")
  try:
    tg_html = fetch_url("https://t.me/s/happvpn")
  except Exception as e:
    print(f"Telegram bağlantı hatası: {e}")
    return

  happ_matches = re.findall(r"happ://[^\s<>\"']+", tg_html)
  if not happ_matches:
    print("Hiç happ linki bulunamadı.")
    return

  latest_happ = happ_matches[-1].replace("&amp;", "&").strip()
  print(f"Bulunan son happ link: {latest_happ}")

  # happ-decryptor içindeki gerçek decoder mantığını Node.js ile çalıştıran köprü kod
  js_runner_code = """
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

async function run() {
    const happLink = process.argv[2];
    try {
        const pkgPath = path.resolve('happ-decryptor/package.json');
        let mainFile = 'src/index.js';
        if (fs.existsSync(pkgPath)) {
            const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
            if (pkg.main) mainFile = pkg.main;
        }
        
        const possiblePaths = [
            path.resolve('happ-decryptor', mainFile),
            path.resolve('happ-decryptor/src/utils/decoder.js'),
            path.resolve('happ-decryptor/src/decoder.js'),
            path.resolve('happ-decryptor/index.js')
        ];
        
        let decoded = "";
        for (let p of possiblePaths) {
            if (fs.existsSync(p)) {
                const mod = await import(pathToFileURL(p).href);
                const decryptFn = mod.decrypt || mod.default || (typeof mod === 'function' ? mod : null);
                if (decryptFn) {
                    decoded = decryptFn(happLink);
                    break;
                }
            }
        }
        
        console.log("DECODED_OUTPUT_START");
        console.log(typeof decoded === 'object' ? JSON.stringify(decoded) : decoded);
        console.log("DECODED_OUTPUT_END");
    } catch (err) {
        console.log("DECODED_OUTPUT_START");
        console.log("HATA: " + err.message);
        console.log("DECODED_OUTPUT_END");
    }
}
run();
"""

  with open("temp_decoder.js", "w", encoding="utf-8") as f:
    f.write(js_runner_code)

  print("Repodaki gerçek decoder çalıştırılıyor...")
  decrypted_text = ""
  try:
    result = subprocess.run(
        ["node", "temp_decoder.js", latest_happ],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
    if "DECODED_OUTPUT_START" in output and "DECODED_OUTPUT_END" in output:
      decrypted_text = output.split("DECODED_OUTPUT_START")[1].split(
          "DECODED_OUTPUT_END"
      )[0]
  except Exception as e:
    print(f"Decoder çalıştırma hatası: {e}")
  finally:
    if os.path.exists("temp_decoder.js"):
      os.remove("temp_decoder.js")

  decrypted_text = decrypted_text.strip()
  print(
      "Çözülen Veri Önizlemesi:"
      f" {decrypted_text[:100]}..."
  )

  # Çözülen metinden https abonelik linkini yakala
  target_url = None
  https_matches = re.findall(r"https?://[^\s<>\"']+", decrypted_text)
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
    print(f"Bulunan abonelik URL'si: {target_url}")
    try:
      sub_content = fetch_url(target_url)
    except Exception as e:
      print(f"Abonelik URL çekilemedi: {e}")
  else:
    sub_content = decrypted_text

  # Çekilen abonelik içeriğindeki node'ları ayıkla
  raw_configs = re.findall(
      r"(?:vless|vmess|ss|trojan)://[^\s<>\"']+", sub_content
  )
  if not raw_configs:
    # Eğer düz metinde çıkmazsa belki base64 encoded donduruyordur abonelik
    try:
      import base64

      decoded_sub = base64.b64decode(sub_content.strip()).decode("utf-8")
      raw_configs = re.findall(
          r"(?:vless|vmess|ss|trojan)://[^\s<>\"']+", decoded_sub
      )
    except:
      pass

  print(f"Toplam ham node sayısı: {len(raw_configs)}")
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
        f"BAŞARILI: Toplam {len(final_links)} adet optimize node dosyaya"
        " yazıldı."
    )
  else:
    print("1500ms altında uygun node bulunamadı.")


if __name__ == "__main__":
  main()
