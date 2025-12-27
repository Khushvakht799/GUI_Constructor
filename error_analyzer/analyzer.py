#!/usr/bin/env python3
"""
Анализатор ошибок Python

Принимает текстовый файл с ошибками Python,
анализирует их и добавляет в базу данных паттернов.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Импортируем наш парсер
try:
    from core.error_parser import ErrorParser, parse_error_file
except ImportError:
    # Для случая, если запускаем из корня проекта
    import sys
    sys.path.append(str(Path(__file__).parent))
    from core.error_parser import ErrorParser, parse_error_file


class ErrorAnalyzer:
    """Анализатор ошибок Python"""
    
    def __init__(self, patterns_db_path: str = "data/error_patterns.json"):
        """
        Инициализация анализатора
        
        Args:
            patterns_db_path: путь к файлу с паттернами ошибок
        """
        self.patterns_db_path = Path(patterns_db_path)
        self.parser = ErrorParser()
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Загрузка паттернов из JSON файла"""
        if self.patterns_db_path.exists():
            try:
                with open(self.patterns_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Инициализируем структуру если её нет
                if "patterns" not in data:
                    data["patterns"] = []
                if "statistics" not in data:
                    data["statistics"] = {"total_errors": 0}
                if "metadata" not in data:
                    data["metadata"] = {}
                
                return data
            except json.JSONDecodeError:
                print(f"Ошибка чтения JSON файла: {self.patterns_db_path}")
                return self._create_empty_patterns_db()
        else:
            return self._create_empty_patterns_db()
    
    def _create_empty_patterns_db(self) -> Dict[str, Any]:
        """Создание пустой структуры базы данных"""
        return {
            "patterns": [],
            "statistics": {
                "total_errors": 0,
                "last_updated": None,
                "pattern_counts": {},
                "files_processed": 0
            },
            "metadata": {
                "version": "1.0.0",
                "description": "База данных паттернов ошибок Python",
                "created_date": datetime.now().isoformat()
            }
        }
    
    def _save_patterns(self):
        """Сохранение паттернов в JSON файл"""
        # Создаем директорию если её нет
        self.patterns_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Обновляем метаданные
        self.patterns["statistics"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.patterns_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False, ensure_ascii=False)
    
    def _find_pattern(self, error_type: str, message: str) -> Dict:
        """Поиск существующего паттерна по типу и сообщению"""
        for pattern in self.patterns["patterns"]:
            if (pattern.get("error_type") == error_type and 
                pattern.get("message_pattern") in message):
                return pattern
        return None
    
    def _create_pattern_from_error(self, error: Dict) -> Dict:
        """Создание нового паттерна из ошибки"""
        # Извлекаем ключевые слова из сообщения
        message = error.get("message", "")
        words = message.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in ["the", "and", "for", "with"]]
        
        # Создаем регулярное выражение для похожих сообщений
        # (упрощенная версия - можно улучшить)
        message_pattern = ".*" + ".*".join(keywords[:3]) + ".*" if keywords else ".*"
        
        return {
            "error_type": error.get("error_type"),
            "message_pattern": message_pattern,
            "examples": [error],
            "solutions": self._generate_suggestions(error),
            "frequency": 1,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
    
    def _generate_suggestions(self, error: Dict) -> List[str]:
        """Генерация предложений по исправлению на основе типа ошибки"""
        error_type = error.get("error_type", "")
        message = error.get("message", "").lower()
        
        suggestions = []
        
        if "import" in error_type or "module" in message:
            suggestions.extend([
                "Проверьте правильность имени модуля",
                "Установите недостающий пакет: pip install <имя_пакета>",
                "Проверьте путь импорта и структуру проекта"
            ])
        elif "syntax" in error_type:
            suggestions.extend([
                "Проверьте закрытие скобок, кавычек, двоеточий",
                "Убедитесь в правильности отступов",
                "Проверьте использование зарезервированных слов"
            ])
        elif "name" in error_type:
            suggestions.extend([
                "Проверьте объявление переменной/функции",
                "Убедитесь в правильности области видимости",
                "Проверьте опечатки в имени"
            ])
        elif "indentation" in error_type:
            suggestions.extend([
                "Приведите отступы к единому стилю (пробелы или табы)",
                "Проверьте количество пробелов в отступах",
                "Используйте автоматическое форматирование кода"
            ])
        else:
            suggestions.append("Проанализируйте контекст ошибки и проверьте типы данных")
        
        return suggestions
    
    def add_to_database(self, parsed_errors: List[Dict[str, Any]]):
        """
        Добавление распарсенных ошибок в базу данных
        
        Args:
            parsed_errors: список распарсенных ошибок
        """
        if not parsed_errors:
            print("Нет ошибок для добавления")
            return
        
        print(f"\nДобавление {len(parsed_errors)} ошибок в базу данных...")
        
        for error in parsed_errors:
            error_type = error.get("error_type")
            message = error.get("message", "")
            
            # Ищем существующий паттерн
            existing_pattern = self._find_pattern(error_type, message)
            
            if existing_pattern:
                # Обновляем существующий паттерн
                existing_pattern["examples"].append(error)
                existing_pattern["frequency"] += 1
                existing_pattern["last_seen"] = datetime.now().isoformat()
                
                # Обновляем статистику
                pattern_key = f"{error_type}_{existing_pattern['message_pattern']}"
                self.patterns["statistics"]["pattern_counts"][pattern_key] = \
                    self.patterns["statistics"]["pattern_counts"].get(pattern_key, 0) + 1
            else:
                # Создаем новый паттерн
                new_pattern = self._create_pattern_from_error(error)
                self.patterns["patterns"].append(new_pattern)
                
                # Обновляем статистику
                pattern_key = f"{error_type}_{new_pattern['message_pattern']}"
                self.patterns["statistics"]["pattern_counts"][pattern_key] = 1
            
            # Обновляем общую статистику
            self.patterns["statistics"]["total_errors"] += 1
        
        self.patterns["statistics"]["files_processed"] += 1
        self._save_patterns()
        
        print(f"✅ База данных обновлена")
        print(f"   Всего ошибок в базе: {self.patterns['statistics']['total_errors']}")
        print(f"   Уникальных паттернов: {len(self.patterns['patterns'])}")
    
    def analyze(self, error_file_path: str):
        """
        Основной метод анализа
        
        Args:
            error_file_path: путь к файлу с ошибками
        """
        print(f"🔍 Запуск анализатора ошибок...")
        print(f"📄 Файл с ошибками: {error_file_path}")
        print(f"🗄️  База паттернов: {self.patterns_db_path}")
        
        # Парсим ошибки
        parsed_errors = parse_error_file(error_file_path)
        
        if not parsed_errors:
            print("❌ Не удалось распарсить ошибки из файла")
            print("   Проверьте формат файла и наличие ошибок Python")
            return
        
        print(f"📊 Распарсено ошибок: {len(parsed_errors)}")
        
        # Показываем типы найденных ошибок
        error_types = {}
        for error in parsed_errors:
            etype = error.get("error_type", "unknown")
            error_types[etype] = error_types.get(etype, 0) + 1
        
        print("📈 Распределение по типам:")
        for etype, count in error_types.items():
            print(f"   {etype}: {count}")
        
        # Добавляем в базу данных
        self.add_to_database(parsed_errors)
        
        print("\n✅ Анализ завершен!")


def main():
    """Точка входа"""
    if len(sys.argv) < 2:
        print("Использование: python analyzer.py <путь_к_файлу_с_ошибками>")
        print("Пример: python analyzer.py errors.txt")
        print("\nДополнительные опции:")
        print("  --db <путь>  Указать путь к базе данных")
        sys.exit(1)
    
    error_file = sys.argv[1]
    db_path = "data/error_patterns.json"
    
    # Обработка дополнительных аргументов
    if len(sys.argv) > 2:
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "--db" and i + 1 < len(sys.argv):
                db_path = sys.argv[i + 1]
    
    # Проверяем существование файла
    if not Path(error_file).exists():
        print(f"❌ Файл не найден: {error_file}")
        sys.exit(1)
    
    # Запускаем анализатор
    analyzer = ErrorAnalyzer(db_path)
    analyzer.analyze(error_file)


if __name__ == "__main__":
    main()
