import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

translations = {
    "en": json.load(open(BASE_DIR / "en.json", encoding="utf-8")),
    "ru": json.load(open(BASE_DIR / "ru.json", encoding="utf-8")),
}


def get_text(key: str, locale: str = "en") -> str:
    return translations.get(locale, translations["en"]).get(key, key)