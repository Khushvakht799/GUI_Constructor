import subprocess
from pathlib import Path

# Каталог проекта с твоими файлами
project_dir = Path("C:/Users/Usuario/GUI_Constructor/src")

# Файл для записи всех ошибок
errors_file = Path("all_errors.txt")

# Очищаем файл перед запуском
errors_file.write_text("", encoding="utf-8")

# Проходим по всем .py файлам рекурсивно, исключая venv, __pycache__ и скрытые папки
py_files = [
    f for f in project_dir.rglob("*.py")
    if "venv" not in f.parts and "__pycache__" not in f.parts and not f.name.startswith(".")
]

for py_file in py_files:
    print(f"🔹 Запуск: {py_file}")
    try:
        # Запуск файла
        result = subprocess.run(
            ["python", str(py_file)],
            capture_output=True,
            text=True,
            timeout=10  # таймаут, чтобы не зависло
        )
        
        # Если есть ошибки (stderr не пустой)
        if result.stderr.strip():
            with open(errors_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Файл: {py_file} ===\n")
                f.write(result.stderr)
                f.write("\n" + "="*50 + "\n")
            print(f"❌ Ошибка сохранена для {py_file}")
        else:
            print(f"✅ {py_file} выполнен без ошибок")

    except subprocess.TimeoutExpired:
        print(f"⏱️  Таймаут при запуске {py_file}")

print(f"✅ Все ошибки собраны в '{errors_file}'")
