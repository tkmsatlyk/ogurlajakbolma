import os
import subprocess


def main():
  print("--- 2. Adım: Kod Deşifre Ediliyor (Dinamik Tarama) ---")
  if not os.path.exists("latest_happ.txt"):
    print("HATA: latest_happ.txt dosyası bulunamadı!")
    return

  with open("latest_happ.txt", "r", encoding="utf-8") as f:
    latest_happ = f.read().strip()

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

  # Repodaki tüm JS dosyalarını tarayıp decrypt fonksiyonunu otomatik bulan köprü script
  js_runner_code = f"""
import fs from 'fs';
import path from 'path';
import {{ pathToFileURL }} from 'url';

function getAllJsFiles(dir, fileList = []) {{
    const files = fs.readdirSync(dir);
    files.forEach(file => {{
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {{
            if (file !== 'node_modules' && file !== '.git') {{
                getAllJsFiles(filePath, fileList);
            }}
        }} else if (file.endsWith('.js')) {{
            fileList.push(filePath);
        }}
    }});
    return fileList;
}}

async function run() {{
    const happLink = "{latest_happ}";
    try {{
        const decFolder = path.resolve('happ-decryptor');
        const jsFiles = getAllJsFiles(decFolder);
        console.log("Taranan JS dosyası sayısı:", jsFiles.length);

        let decoded = "";
        let found = false;

        for (const file of jsFiles) {{
            try {{
                const mod = await import(pathToFileURL(file).href);
                const decryptFn = mod.decrypt || mod.default || (typeof mod === 'function' ? mod : null);
                if (decryptFn) {{
                    console.log("Decoder fonksiyonu şurada bulundu:", path.relative(decFolder, file));
                    const res = decryptFn(happLink);
                    if (res) {{
                        decoded = res;
                        found = true;
                        break;
                    }}
                }}
            }} catch (e) {{
                // Bazı dosyalar bağımlılık veya test dosyası olabilir, geçiyoruz
            }}
        }}

        if (!found) {{
            console.log("HATA: Hiçbir modülde geçerli decrypt fonksiyonu çalıştırılamadı.");
        }}

        console.log("DECODE_OK_START");
        console.log(typeof decoded === 'object' ? JSON.stringify(decoded) : decoded);
        console.log("DECODE_OK_END");
    }} catch (err) {{
        console.log("DECODE_OK_START");
        console.log("JS HATA: " + err.message);
        console.log("DECODE_OK_END");
    }}
}}
run();
"""

  with open("temp_decoder.js", "w", encoding="utf-8") as f:
    f.write(js_runner_code)

  print("Dinamik decoder çalıştırılıyor...")
  decoded_text = ""
  try:
    result = subprocess.run(
        ["node", "temp_decoder.js"], capture_output=True, text=True, check=True
    )
    print(result.stdout)
    output = result.stdout
    if "DECODE_OK_START" in output and "DECODE_OK_END" in output:
      decoded_text = output.split("DECODE_OK_START")[1].split(
          "DECODE_OK_END"
      )[0].strip()
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
