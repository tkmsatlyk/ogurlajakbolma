from pathlib import Path

NAMES_FILE = Path("names.txt")
OUTPUT_FILE = Path("output/configs.txt")


def load_names():
    if not NAMES_FILE.exists():
        raise FileNotFoundError("names.txt bulunamadı.")

    return [
        line.strip()
        for line in NAMES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main():
    names = load_names()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Eski configs.txt tamamen silinir ve yeniden oluşturulur.
    lines = []

    for name in names:
        lines.append(name)
        lines.append("# TEST_CONFIG")
        lines.append("")

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(f"{len(names)} isim işlendi.")
    print(f"Yeni dosya oluşturuldu: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
