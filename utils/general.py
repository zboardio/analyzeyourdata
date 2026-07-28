import json
from pathlib import Path
from config import Config

# Load markdown variables once at import time
_markdown_variables = {}
_variables_path = Path(__file__).parent.parent / 'assets' / 'markdown' / 'master' / 'variables.json'
if _variables_path.exists():
    with open(_variables_path, 'r', encoding='utf-8') as _f:
        _markdown_variables = json.load(_f)


def get_variable(key, default=''):
    """Get a value from the markdown variables dict (assets/markdown/master/variables.json)."""
    return _markdown_variables.get(key, default)


def _resolve_variables(content):
    """Replace {{VARIABLE}} placeholders with values from masters/variables.json."""
    for key, value in _markdown_variables.items():
        content = content.replace('{{' + key + '}}', value)
    return content


def load_markdown_file(filename, subdirectory=None):
    """
    Load Markdown content from the configured markdown directory with language-aware resolution.

    Fallback chain:
    1. markdown/{lang}/{subdirectory}/{filename}
    2. markdown/en/{subdirectory}/{filename}  (English fallback if lang != 'en')
    3. markdown/{lang}/404.md
    4. markdown/en/404.md
    5. Hardcoded 404 message

    Parameters:
    - filename (str): Name of the markdown file to load (e.g., 'info.md').
    - subdirectory (str, optional): Subdirectory within the language folder (e.g., 'help').

    Returns:
    - str: Content of the markdown file.

    Examples:
    - load_markdown_file("info.md") → loads from assets/markdown/en/info.md
    - load_markdown_file("guide.md", "help") → loads from assets/markdown/en/help/guide.md
    """
    base_path = Path(Config.MARKDOWN_DIRECTORY)
    lang = Config.APP_LANGUAGE

    # Build candidate paths in priority order
    def build_path(language, sub, name):
        if sub:
            return base_path / language / sub / name
        return base_path / language / name

    # 1. Try requested language
    file_path = build_path(lang, subdirectory, filename)
    if file_path.exists():
        return _read_file(file_path)

    # 2. Fallback to English (if not already English)
    if lang != 'en':
        file_path = build_path('en', subdirectory, filename)
        if file_path.exists():
            return _read_file(file_path)

    # 3. Language-specific 404
    fallback_path = base_path / lang / '404.md'
    if fallback_path.exists():
        return _read_file(fallback_path)

    # 4. English 404
    fallback_path = base_path / 'en' / '404.md'
    if fallback_path.exists():
        return _read_file(fallback_path)

    # 5. Hardcoded fallback
    return "#### 404 Markdown file not found\n**The requested file is not accessible.**"


def _read_file(file_path):
    """Read a file, resolve {{VARIABLE}} placeholders, and return contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return _resolve_variables(file.read())
    except Exception as e:
        return f"#### Error loading markdown file\n**Error: {str(e)}**"

