import json
from pathlib import Path

from config import Config

_translations = {}


def load_translations(lang_code=None):
    """Load translation strings from JSON file for the given language."""
    global _translations
    lang = lang_code or Config.APP_LANGUAGE
    i18n_dir = Path(__file__).parent

    for try_lang in ([lang, 'en'] if lang != 'en' else ['en']):
        lang_file = i18n_dir / f'{try_lang}.json'
        if lang_file.exists():
            with open(lang_file, 'r', encoding='utf-8') as f:
                _translations = json.load(f)
            return


def t(key, **kwargs):
    """Get translated string by key. Falls back to key itself if not found."""
    text = _translations.get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


# Auto-load at import time
load_translations()
