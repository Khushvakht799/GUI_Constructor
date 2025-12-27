"""
Конфигурация анализатора ошибок
"""

from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PATTERNS_DB = DATA_DIR / "error_patterns.json"

# Настройки парсинга
ERROR_PATTERNS = {
    "import_error": r"ModuleNotFoundError|ImportError",
    "syntax_error": r"SyntaxError",
    "name_error": r"NameError",
    "type_error": r"TypeError",
    "indentation_error": r"IndentationError",
}

# Максимальное количество сохраняемых примеров для каждого паттерна
MAX_EXAMPLES_PER_PATTERN = 10

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "analysis.log"
