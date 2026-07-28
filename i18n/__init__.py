import json
from pathlib import Path

from config import Config

_translations = {}
_fallback = {}


def load_translations(lang_code=None):
    """Load translation strings for the given language, plus English fallback."""
    global _translations, _fallback
    lang = lang_code or Config.APP_LANGUAGE
    i18n_dir = Path(__file__).parent

    en_file = i18n_dir / 'en.json'
    if en_file.exists():
        with open(en_file, 'r', encoding='utf-8') as f:
            _fallback = json.load(f)

    lang_file = i18n_dir / f'{lang}.json'
    if lang == 'en' or not lang_file.exists():
        _translations = _fallback
    else:
        with open(lang_file, 'r', encoding='utf-8') as f:
            _translations = json.load(f)


def t(key, **kwargs):
    """Get translated string by key.

    Missing keys fall back to English, then to the key itself. Interpolation
    never raises: on a placeholder mismatch the raw string is returned, so a
    broken translation can't crash a render (t() runs at import time for
    layout strings).
    """
    text = _translations.get(key) or _fallback.get(key) or key
    if kwargs and isinstance(text, str):
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass
    return text


def load_aggrid_locale(lang_code=None):
    """Load the AG Grid localeText dict for the language.

    Returns {} for English (AG Grid's built-in defaults) and for unknown
    languages. Keys missing from a language file fall back to AG Grid's
    defaults per key, so partial dictionaries (e.g. Slovenian) are fine.
    """
    lang = lang_code or Config.APP_LANGUAGE
    if lang == 'en':
        return {}
    locale_file = Path(__file__).parent / 'aggrid' / f'{lang}.json'
    if not locale_file.exists():
        return {}
    with open(locale_file, 'r', encoding='utf-8') as f:
        return json.load(f)


# Auto-load at import time
load_translations()
