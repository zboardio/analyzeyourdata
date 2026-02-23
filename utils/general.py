import json
import os
import re
from pathlib import Path
from config import Config

# Load markdown variables once at import time
_markdown_variables = {}
_variables_path = Path(__file__).parent.parent / 'assets' / 'markdown' / 'master' / 'variables.json'
if _variables_path.exists():
    with open(_variables_path, 'r', encoding='utf-8') as _f:
        _markdown_variables = json.load(_f)


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

def load_markdown(directory, filename):
    """
    Legacy function for backward compatibility.
    Load Markdown content from a specified directory and file.

    Parameters:
    - directory (str): Path to the folder containing the markdown file.
    - filename (str): Name of the markdown file to load (e.g., 'example.md').

    Returns:
    - str: Content of the markdown file. If the file doesn't exist, falls back to language-aware 404.
    """
    file_path = Path(directory) / filename

    if not file_path.exists():
        # Use language-aware 404 fallback
        return load_markdown_file('404.md')

    return _read_file(file_path)

def create_output_directory_specification(base_path, plant_area):
    """
    Creates a structured output directory specification based on a base path and plant area identifier.

    Parameters:
    - base_path (str): The root directory where the output path will be created.
    - plant_area (str): A string representing the plant area, which can include
                        special codes, underscores, and mixed-case letters.

    Returns:
    - str: The full path to the created output directory.
    """
    # Regular expression to identify special patterns
    special_pattern = re.compile(r'^\d{3}[A-Z]\d{4}(_\d+)?$')
    # Split the plant_area string into components
    parts = plant_area.split('/')
    output_path = base_path

    for part in parts:
        if special_pattern.match(part):
            # Keep parts matching the special pattern unchanged
            sanitized_part = part
        elif "_" in part:
            # Convert parts with underscores to lowercase
            sanitized_part = part.lower()
        elif any(c.isdigit() for c in part):
            # Preserve uppercase letters and digits; lowercase other letters
            sanitized_part = "".join(
                [c if c.isupper() or c.isdigit() else c.lower() for c in part]
            )
        else:
            # Lowercase any other parts
            sanitized_part = part.lower()

        # Construct the output path incrementally
        output_path = os.path.join(output_path, sanitized_part)
        # Create the directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

    return output_path

def flatten_nested_dict(data, parent_key='', sep=' | '):
    """
    Recursively flattens a nested dictionary, combining keys with a specified separator.

    This function takes a nested dictionary as input and produces a single-level dictionary
    where nested keys are concatenated into a single string with a separator. This is useful
    for flattening deeply nested data structures for easier representation or storage in formats
    like tables.

    Parameters:
    -----------
    data : dict
        The nested dictionary to flatten.
    parent_key : str, optional
        The base key to prefix flattened keys with, used for recursion (default is an empty string).
    sep : str, optional
        The separator used to combine parent and child keys (default is '|').

    Returns:
    --------
    dict
        A flattened dictionary with concatenated keys and corresponding values.

    Examples:
    ---------
    >>> data = {
    ...     "key1": {
    ...         "subkey1": {
    ...             "subsubkey1": "value1",
    ...             "subsubkey2": "value2"
    ...         },
    ...         "subkey2": "value3"
    ...     },
    ...     "key2": "value4"
    ... }
    >>> flatten_nested_dict(data)
    {
        'key1|subkey1|subsubkey1': 'value1',
        'key1|subkey1|subsubkey2': 'value2',
        'key1|subkey2': 'value3',
        'key2': 'value4'
    }

    Notes:
    ------
    - The separator can be customized for specific use cases (e.g., '.' for dot notation).
    - Handles dictionaries with multiple levels of nesting.
    """
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_nested_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)