import json
from pathlib import Path

import pytest

import i18n

I18N_DIR = Path(i18n.__file__).parent
LANGUAGES = ['en', 'cs', 'da', 'de', 'es', 'fr', 'hr', 'it', 'nl', 'pl', 'pt', 'sk', 'sl', 'sv', 'uk']


@pytest.fixture(autouse=True)
def restore_translations():
    """Every test starts from and returns to the default (English) state."""
    i18n.load_translations('en')
    yield
    i18n.load_translations('en')


def test_all_language_files_exist_and_parse():
    for lang in LANGUAGES:
        data = json.loads((I18N_DIR / f'{lang}.json').read_text(encoding='utf-8'))
        assert isinstance(data, dict) and data


def test_all_language_files_have_same_keys():
    reference = set(json.loads((I18N_DIR / 'en.json').read_text(encoding='utf-8')))
    for lang in LANGUAGES:
        keys = set(json.loads((I18N_DIR / f'{lang}.json').read_text(encoding='utf-8')))
        assert keys == reference, f'{lang}.json keys differ from en.json'


def test_translation_lookup():
    i18n.load_translations('cs')
    assert i18n.t('data_source.upload') != 'data_source.upload'


def test_missing_key_returns_key():
    assert i18n.t('nonexistent.key.xyz') == 'nonexistent.key.xyz'


def test_missing_key_falls_back_to_english():
    i18n.load_translations('cs')
    del i18n._translations['data_source.upload']
    assert i18n.t('data_source.upload') == i18n._fallback['data_source.upload']


def test_interpolation():
    assert '20' in i18n.t('data_source.step1_heading', max_size=20)


def test_broken_placeholder_does_not_raise():
    i18n._translations['broken.key'] = 'Value {missing} and {other}'
    assert i18n.t('broken.key', wrong=1) == 'Value {missing} and {other}'


def test_loose_brace_does_not_raise():
    i18n._translations['brace.key'] = 'Loose { brace'
    assert i18n.t('brace.key', x=1) == 'Loose { brace'


def test_unknown_language_falls_back_to_english():
    i18n.load_translations('xx')
    assert i18n.t('data_source.upload') == i18n._fallback['data_source.upload']


class TestAgGridLocale:
    def test_english_uses_grid_defaults(self):
        assert i18n.load_aggrid_locale('en') == {}

    def test_unknown_language_empty(self):
        assert i18n.load_aggrid_locale('xx') == {}

    def test_official_locales_load(self):
        for lang in ['cs', 'da', 'de', 'es', 'fr', 'hr', 'it', 'nl', 'pl', 'pt', 'sk', 'sv', 'uk']:
            locale = i18n.load_aggrid_locale(lang)
            assert len(locale) > 400, f'{lang} grid locale unexpectedly small'
            assert 'filterOoo' in locale

    def test_slovenian_curated_subset(self):
        locale = i18n.load_aggrid_locale('sl')
        assert 100 < len(locale) < 400
        assert locale['filterOoo'] == 'Filtriraj...'

    def test_locale_values_are_strings(self):
        for lang in ['cs', 'sl', 'uk']:
            for key, value in i18n.load_aggrid_locale(lang).items():
                assert isinstance(value, str), f'{lang}:{key} is not a string'
