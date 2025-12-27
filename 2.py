import re

# Файл с "сырыми" строками ошибок
input_file = "errors_only.txt"
# Файл для записи систематизированного вывода
output_file = "errors_numbered.txt"

# Ключевые слова для классификации ошибок
error_keywords = ["ImportError", "Exception", "Error", "FAILED", "warning", "INVALID", "Traceback"]

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

with open(output_file, "w", encoding="utf-8") as f_out:
    for i, line in enumerate(lines, 1):
        line_clean = line.strip()
        if not line_clean:
            continue
        # Ищем тип ошибки по ключевым словам
        found_types = [kw for kw in error_keywords if re.search(kw, line_clean, re.IGNORECASE)]
        error_type = found_types[0] if found_types else "Other"
        # Записываем зеркально: номер | текст | тип
        f_out.write(f"{i} | {line_clean} | {error_type}\n")

print(f"✅ Систематизация завершена. Результат в '{output_file}'")
