"""
Парсер ошибок Python

Модуль для парсинга различных форматов ошибок Python из текстовых файлов.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class ParsedError:
    """Структура для хранения распарсенной ошибки"""
    error_type: str           # Тип ошибки: ImportError, SyntaxError и т.д.
    message: str             # Сообщение об ошибке
    file_path: Optional[str] # Путь к файлу где возникла ошибка
    line_number: Optional[int] # Номер строки
    code_snippet: Optional[str] # Фрагмент кода с ошибкой
    full_traceback: str      # Полный traceback
    timestamp: Optional[str] # Время возникновения (если есть)
    
    def to_dict(self) -> Dict:
        """Конвертация в словарь для JSON"""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "full_traceback": self.full_traceback,
            "timestamp": self.timestamp
        }


class ErrorParser:
    """Парсер ошибок Python из различных форматов"""
    
    # Регулярные выражения для распознавания ошибок
    ERROR_PATTERNS = {
        "import_error": r"(ModuleNotFoundError|ImportError):\s*(.*)",
        "syntax_error": r"SyntaxError:\s*(.*)",
        "name_error": r"NameError:\s*(.*)",
        "type_error": r"TypeError:\s*(.*)",
        "indentation_error": r"IndentationError:\s*(.*)",
        "value_error": r"ValueError:\s*(.*)",
        "key_error": r"KeyError:\s*(.*)",
        "attribute_error": r"AttributeError:\s*(.*)",
        "index_error": r"IndexError:\s*(.*)",
    }
    
    # Паттерн для извлечения пути к файлу и номера строки
    FILE_LINE_PATTERN = r'File\s+"([^"]+)",\s*line\s+(\d+)'
    
    def __init__(self):
        self.compiled_patterns = {
            name: re.compile(pattern) 
            for name, pattern in self.ERROR_PATTERNS.items()
        }
        self.file_line_pattern = re.compile(self.FILE_LINE_PATTERN)
    
    def parse_file(self, file_path: str) -> List[ParsedError]:
        """
        Парсинг файла с ошибками
        
        Args:
            file_path: путь к файлу с ошибками
            
        Returns:
            Список распарсенных ошибок
        """
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разделяем на отдельные traceback'и
            tracebacks = self._split_into_tracebacks(content)
            
            for tb in tracebacks:
                error = self._parse_traceback(tb)
                if error:
                    errors.append(error)
                    
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
        
        return errors
    
    def _split_into_tracebacks(self, content: str) -> List[str]:
        """
        Разделение содержимого на отдельные traceback'и
        
        Args:
            content: полное содержимое файла
            
        Returns:
            Список traceback'ов
        """
        # Простая эвристика: разделяем по пустым строкам или началу нового traceback
        lines = content.split('\n')
        tracebacks = []
        current_tb = []
        
        for line in lines:
            if line.strip() == '' and current_tb:
                # Пустая строка - возможный разделитель
                if current_tb:
                    tracebacks.append('\n'.join(current_tb))
                    current_tb = []
            else:
                current_tb.append(line)
        
        # Добавляем последний traceback если есть
        if current_tb:
            tracebacks.append('\n'.join(current_tb))
        
        return tracebacks
    
    def _parse_traceback(self, traceback: str) -> Optional[ParsedError]:
        """
        Парсинг одного traceback'а
        
        Args:
            traceback: текст traceback'а
            
        Returns:
            ParsedError или None если не удалось распарсить
        """
        lines = traceback.strip().split('\n')
        if not lines:
            return None
        
        # Ищем строку с ошибкой (обычно последняя или предпоследняя)
        error_line = None
        for line in reversed(lines):
            for error_name, pattern in self.compiled_patterns.items():
                match = pattern.search(line)
                if match:
                    error_line = line
                    error_type = error_name
                    break
            if error_line:
                break
        
        if not error_line:
            return None
        
        # Извлекаем информацию о файле и строке
        file_path = None
        line_number = None
        for line in lines:
            match = self.file_line_pattern.search(line)
            if match:
                file_path = match.group(1)
                line_number = int(match.group(2))
                break
        
        # Извлекаем сообщение об ошибке
        message = self._extract_error_message(error_line)
        
        # Извлекаем фрагмент кода если есть
        code_snippet = self._extract_code_snippet(lines, line_number)
        
        return ParsedError(
            error_type=error_type,
            message=message,
            file_path=file_path,
            line_number=line_number,
            code_snippet=code_snippet,
            full_traceback=traceback,
            timestamp=self._extract_timestamp(traceback)
        )
    
    def _extract_error_message(self, error_line: str) -> str:
        """Извлечение сообщения об ошибке из строки"""
        # Убираем тип ошибки из начала
        for error_type in self.ERROR_PATTERNS.keys():
            if error_line.startswith(error_type):
                return error_line[len(error_type):].strip(': ')
        
        # Если не нашли по началу, ищем двоеточие
        if ':' in error_line:
            return error_line.split(':', 1)[1].strip()
        
        return error_line.strip()
    
    def _extract_code_snippet(self, lines: List[str], line_num: Optional[int]) -> Optional[str]:
        """Извлечение фрагмента кода вокруг ошибки"""
        if not line_num:
            return None
        
        # Ищем строку с кодом (обычно содержит указатель ^)
        for i, line in enumerate(lines):
            if '^' in line and any(str(line_num) in lines[i-1] for j in range(max(0, i-2), i)):
                # Возвращаем строку с кодом и указателем
                return '\n'.join(lines[max(0, i-2):min(len(lines), i+2)])
        
        return None
    
    def _extract_timestamp(self, traceback: str) -> Optional[str]:
        """Извлечение временной метки из traceback"""
        # Простая эвристика для формата timestamp
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, traceback)
            if match:
                return match.group(0)
        
        return None


# Утилитарные функции
def parse_error_file(file_path: str) -> List[Dict]:
    """Упрощенный интерфейс для парсинга файла с ошибками"""
    parser = ErrorParser()
    errors = parser.parse_file(file_path)
    return [error.to_dict() for error in errors]


if __name__ == "__main__":
    # Тестирование парсера
    test_traceback = '''
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    import nonexistent_module
ModuleNotFoundError: No module named 'nonexistent_module'
'''
    
    parser = ErrorParser()
    result = parser._parse_traceback(test_traceback)
    print(f"Парсинг тестового traceback: {result}")
