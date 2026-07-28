import sys
from pathlib import Path

# Make top-level modules (config, i18n, utils, ...) importable from tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
