import os
import subprocess


def main():
  print("--- 2. Adım: Kod Deşifre Ediliyor ---")
  if not os.path.exists("latest_happ.txt"):
    print("Hata: latest_happ.txt dosyası bulunamadı!")
    return

  with open("latest_happ.txt", "r", encoding="utf-8") as f:
    latest_happ = f.read().strip()

  # Repoyu klonla ve eksik npm paketlerini yükle
  if not os.path.exists("happ-decryptor"):
    print("Decryptor deposu klonlanıyor...")
    subprocess.run(
        [
            "git",
            "clone",
            "https://github.com/LeeeeT/happ-decryptor.git",
            "happ-decryptor",
        ],
        check=True,
    )

  print("Decryptor bağımlılıkları yükleniyor (npm install)...")
  subprocess.run(["npm", "install"], cwd="happ-decryptor", check=True)

  # Node.js yardımıyla repodaki decoder motorunu çalıştıran köprü script
  js_runner_code = f"""
import fs from 'fs';
import path from 'path';
import {{ pathToFileURL }} from 'url';

async function run() {{
    const happLink = "{latest_happ}";
    try {{
        const pkgPath = path.resolve('happ-decryptor/package.json');
        let mainFile = 'src/index.js';
        if (fs.existsSync(pkgPath)) {{
            const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
            if (pkg.main) mainFile = pkg.main;
        }}
        
        const possiblePaths = [
            path.resolve('happ-decryptor', mainFile),
            path.resolve('happ-decryptor/src/utils/decoder.js'),
            path.resolve('happ-decryptor/src/decoder.js'),
            path.resolve('happ-decryptor/index.js')
        ];
        
        let decoded = "";
        for (let p of possiblePaths) {{
            if (fs.existsSync(p)) {{
                const mod = await import(pathToFileURL(p).href);
                const decryptFn = mod.decrypt || mod.default || (typeof mod === 'function' ? mod : null);
                if (decryptFn) {{
                    decoded = decryptFn(happLink);
                    break;
                }}
            }}
        }}
        
        console.log("DECODE_OK_START");
        console.log(typeof decoded === 'object' ? JSON.stringify(decoded) : decoded);
        console.log("DECODE_OK_END");
    }} catch (err) {{
        console.log("DECODE_OK_START");
        console.log("HATA: " + err.message);
        console.log("DECODE_OK_END");
    }}
}}
run();
"""

  with open("temp_decoder.js", "w", encoding="utf-8") as f:
    f.write(js_runner_code)

  print("Decoder çalıştırılıyor...")
  decoded_text = ""
  try:
    result = subprocess.run(
        ["node", "temp_decoder.js"], capture_output=True, text=True, check=True
    )
    output = result.stdout
    if "DECODE_OK_START" in output and "DECODE_OK_END" in output:
      decoded_text = output.split("DECODE_OK_START")[1].split("DECODE_OK_END")[
          0
      ].strip()
  except Exception as e:
    print(f"Çalıştırma hatası: {e}")
  finally:
    if os.path.exists("temp_decoder.js"):
      os.remove("temp_decoder.js")

  # Deşifre edilen sonucu diğer dosyaya aktar
  with open("decoded_result.txt", "w", encoding="utf-8") as f:
    f.write(decoded_text)

  print("Başarılı: Deşifre edilen veri decoded_result.txt dosyasına yazıldı.")


if __name__ == "__main__":
  main()
