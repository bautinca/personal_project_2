from pathlib import Path

# La version se define a mano en el archivo VERSION de la raiz del proyecto, la unica fuente de verdad.
VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"


def read_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()
