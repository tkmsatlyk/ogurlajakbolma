import os
import subprocess


def main():
  print("--- 2. Adım: Kod Deşifre Ediliyor (Debug) ---")
  if not os.path.exists("latest_happ.txt"):
    print("HATA: latest_happ.txt dosyası bulunamadı!")
    return

  with open("latest_happ.txt", "r", encoding="utf-8") as f:
    latest_happ = f.read().strip()

  print(f"Okunan happ linki: {latest_happ}")

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

  # İçeriği ve olası export'ları detaylı test eden köprü script
  js_runner_code = f"""
import fs from 'fs';
import path from 'path';
import {{ pathToFileURL }} from 'url';

async function run() {{
    const happLink = "{latest_happ}";
    try {{
        const decFolder = path.resolve('happ-decryptor');
        const files = fs.readdirSync(decFolder);
        console.log("Klonlanan repo dosyaları:", files);

        const pkgPath = path.join(decFolder, 'package.json');
        let mainFile = 'src/index.js';
        if (fs.existsSync(pkgPath)) {{
            const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
            console.log("Package.json main:", pkg.main);
            if (pkg.main) mainFile = pkg.main;
        }}
        
        const targetPath = path.resolve(decFolder, mainFile);
        console.log("Yüklenmeye çalışılan ana dosya:", targetPath);

        if (fs.existsSync(targetPath)) {{
            const mod = await import(pathToFileURL(targetPath).href);
            console.log("Modül export anahtarları:", Object.keys(mod));
            
            const decryptFn = mod.decrypt || mod.default || (typeof mod === 'function' ? mod : null);
            if (decryptFn) {{
                const decoded = decryptFn(happLink);
                console.log("DECODE_OK_START");
                console.log(typeof decoded === 'object' ? JSON.stringify(decoded) : decoded);
                console.log("DECODE_OK_END");
            }} else {{
                console.log("HATA: Modül içinde uygun decrypt fonksiyonu bulunamadı!");
            }}
        }} else {{
            console.log("HATA: Ana dosya diskte bulunamadı!");
        }}
    }} catch (err) {{
        console.log("DECODE_OK_START");
        console.log("JS HATA: " + err.message + " | Stack: " + err.stack);
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
    print("--- Node.js Ham Çıktısı Başlangıcı ---")
    print(result.stdout)
    print("--- Node.js Ham Çıktısı Sonu ---")

    output = result.stdout
    if "DECODE_OK_START" in output and "DECODE_OK_END" in output:
      decoded_text = output.split("DECODE_OK_START")[1].split("DECODE_OK_END")[
          0
      ].strip()
  except Exception as e:
    print(f"Python Subprocess Hatası: {e}")
  finally:
    if os.path.exists("temp_decoder.js"):
      os.remove("temp_decoder.js")

  with open("decoded_result.txt", "w", encoding="utf-8") as f:
    f.write(decoded_text)

  print(f"Yazılan decoded_text uzunluğu: {len(decoded_text)}")


if __name__ == "__main__":
  main()
