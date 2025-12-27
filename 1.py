# 1.py
file_path = "errors_only.txt"

# Читаем файл с безопасной кодировкой
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# Убираем пустые строки и дубли
unique_lines = sorted(set(line.strip() for line in lines if line.strip()))

# Сохраняем результат в новый файл
with open("errors_sorted.txt", "w", encoding="utf-8") as f:
    for line in unique_lines:
        f.write(line + "\n")

print(f"✅ Получено {len(unique_lines)} уникальных ошибок. Результат в 'errors_sorted.txt'")
