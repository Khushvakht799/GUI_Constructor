import re

# Файл с "сырыми" ошибками от Python
input_file = "all_errors.txt"
# Файл для записи структурированной базы ошибок
output_file = "errors_structured.txt"

# Регулярка для извлечения типа ошибки из строки Python
error_type_re = re.compile(r"^(?P<type>\w+Error|SyntaxError|ImportError):?\s*(?P<msg>.*)")

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Разбиваем на блоки по ========, каждая секция — одна ошибка
blocks = content.split("==================================================")

structured_errors = []

for i, block in enumerate(blocks, 1):
    block = block.strip()
    if not block:
        continue
    lines = block.splitlines()
    # Ищем имя файла
    file_line = next((l for l in lines if l.startswith("=== Файл:")), None)
    if file_line:
        filename = file_line.replace("=== Файл:", "").strip()
    else:
        filename = "Unknown"

    # Ищем первую строку с типом ошибки
    error_line = next((l for l in lines if error_type_re.search(l)), None)
    if error_line:
        match = error_type_re.search(error_line)
        error_type = match.group("type")
        error_msg = match.group("msg").strip()
    else:
        error_type = "Unknown"
        error_msg = " | ".join(lines)

    structured_errors.append(f"{i} | {filename} | {error_type} | {error_msg}")

# Записываем в файл
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(structured_errors))

print(f"✅ База ошибок создана. Результат в '{output_file}'")
