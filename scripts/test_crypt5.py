import os
import subprocess
import sys

link = os.environ.get("HAPP_TEST_LINK")

if not link:
    print("HAPP_TEST_LINK bulunamadı")
    sys.exit(1)

if not link.startswith("happ://crypt5/"):
    print("Bu bir happ://crypt5 linki değil")
    sys.exit(1)

print("crypt5 linki bulundu.")
print("Decryptor çalıştırılıyor...")

result = subprocess.run(
    ["hpwnr", link],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("DECRYPT HATASI:")
    print(result.stderr)
    sys.exit(result.returncode)

print("DECRYPT BAŞARILI")
print(result.stdout)
