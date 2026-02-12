import json
from pathlib import Path


BASE_DIR = Path(__file__).parent
LANGUAGES_FILE = BASE_DIR / "languages.json"


def load_languages() -> dict:
    with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


SUPPORTED_LANGUAGES = load_languages()


def is_supported(locale: str) -> bool:
    return locale in SUPPORTED_LANGUAGES


def get_active_languages() -> dict:
    return {
        code: meta
        for code, meta in SUPPORTED_LANGUAGES.items()
        if meta.get("is_active", True)
    }