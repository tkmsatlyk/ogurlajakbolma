from pathlib import Path
from datetime import datetime, timezone

OUTPUT = Path("output/configs.txt")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Her çalışmada eski dosyayı tamamen temizle.
configs = [
    "# Test başarılı",
    f"# Güncelleme: {datetime.now(timezone.utc).isoformat()}",
]

OUTPUT.write_text(
    "\n".join(configs) + "\n",
    encoding="utf-8"
)

print(f"{OUTPUT} yeniden oluşturuldu.")
