"""
project_analyzer.py

Модуль для GUI_Constructor — этап 1: анализ структуры Python-проекта.

Функции:
- scan_project(path) -> dict: собирает дерево, список py-файлов
- parse_imports(file_path) -> set: извлекает импорты из AST
- build_dependency_graph(py_files) -> dict: граф зависимостей (файл -> set(files it imports))
- detect_cycles(graph) -> list of cycles
- find_entry_points(py_files) -> list of files, содержащих `if __name__ == "__main__"`
- generate_report(path, out_file): сохраняет JSON-отчёт

CLI: python project_analyzer.py /path/to/project

Важно: модуль НЕ изменяет исходники — только читает и создаёт отчёт.
"""

from __future__ import annotations
import os
import ast
import json
from typing import Dict, Set, List, Tuple
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("project_analyzer")


def scan_project(root: str) -> Dict:
    """Сканирует проект, возвращает базовую информацию.

    Результат содержит:
    {
      "root": <abs path>,
      "py_files": [<rel paths>],
      "packages": [<package dirs>],
      "entry_points": [<rel paths>],
      "dependency_graph": {rel_path: [rel_path,...]},
      "cycles": [[a,b,c], ...]
    }
    """
    root_path = Path(root).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    logger.info(f"Scanning project: {root_path}")

    py_files: List[Path] = []
    packages: Set[Path] = set()

    for dirpath, dirnames, filenames in os.walk(root_path):
        p = Path(dirpath)
        if "__pycache__" in dirpath:
            continue
        if "venv" in dirpath or ".venv" in dirpath:
            # пропускаем виртуальные окружения
            continue
        if "node_modules" in dirpath:
            continue
        for fname in filenames:
            if fname.endswith('.py'):
                py_files.append(p / fname)
        # package = присутствие __init__.py
        if (p / "__init__.py").exists():
            packages.add(p)

    # нормализуем относительные пути
    py_files_rel = [str(p.relative_to(root_path)) for p in py_files]

    # извлекаем импорты и строим граф
    dep_graph = build_dependency_graph(py_files, root_path)

    # detect cycles
    cycles = detect_cycles(dep_graph)

    # find entry points
    entries = find_entry_points(py_files, root_path)

    report = {
        "root": str(root_path),
        "py_files": py_files_rel,
        "packages": [str(p.relative_to(root_path)) for p in sorted(packages)],
        "entry_points": entries,
        "dependency_graph": {k: sorted(list(v)) for k, v in dep_graph.items()},
        "cycles": cycles,
    }

    return report


def parse_imports(file_path: Path) -> Set[str]:
    """Возвращает набор импортируемых модулей/имён как строки.

    Пример: 'os', 'sys', 'package.module', 'module.sub'

    Не резолвит локальные файлы в полные пути — это делает функция map_imports_to_files
    """
    imports: Set[str] = set()
    try:
        src = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.debug(f"Failed to read {file_path}: {e}")
        return imports

    try:
        tree = ast.parse(src)
    except SyntaxError:
        # синтаксическая ошибка — вернём пустой набор и позволим верхнему уровню обработать
        logger.debug(f"SyntaxError while parsing {file_path}")
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name)  # пакет или модуль
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module is None:
                # from . import x  или relative import
                # записываем относительный импорт как '.' prefix
                level = node.level if hasattr(node, 'level') else 0
                imports.add('.' * level)
            else:
                imports.add(module)
    return imports


def map_imports_to_files(imports: Set[str], py_files: List[Path], root: Path) -> Set[str]:
    """Пытается сопоставить импортные имена с локальными файлами проекта.

    Возвращает set относительных путей (str) внутри проекта, которые соответствуют импортам.
    Если соответствия нет — импорт будет проигнорирован здесь (внешняя зависимость).
    """
    results: Set[str] = set()
    # подготовим индекс: путь без суффикса .py -> Path
    index: Dict[str, Path] = {}
    for p in py_files:
        rel = p.relative_to(root)
        key = str(rel.with_suffix(''))  # путь/to/module
        # также поддержка package.module -> package/module.py
        index[key.replace(os.sep, '.')] = rel
        index[str(rel)] = rel
    # try to match
    for imp in imports:
        if imp in index:
            results.add(str(index[imp]))
        else:
            # try progressively: a.b.c -> a/b.py or a/b/__init__.py
            parts = imp.split('.')
            for i in range(len(parts), 0, -1):
                candidate1 = Path(os.path.join(*parts[:i])).with_suffix('.py')
                candidate2 = Path(os.path.join(*parts[:i])) / "__init__.py"
                if candidate1.exists():
                    results.add(str(candidate1))
                    break
                if candidate2.exists():
                    results.add(str(candidate2))
                    break
            # если не нашли — возможно внешняя библиотека
    return results


def build_dependency_graph(py_files: List[Path], root: Path) -> Dict[str, Set[str]]:
    """Строит граф зависимостей: файл -> set(локальных модулей, которые он импортирует)

    Вход py_files — список Path объектов с абсолютными путями.
    Возвращает словарь с ключами — относительные пути (str)
    """
    graph: Dict[str, Set[str]] = {}
    for p in py_files:
        rel = str(p.relative_to(root))
        imports = parse_imports(p)
        mapped = map_imports_to_files(imports, py_files, root)
        # нормализуем пути к относительным строкам
        graph[rel] = set()
        for m in mapped:
            try:
                # если m уже относительный Path
                mrel = str(Path(m))
                graph[rel].add(mrel)
            except Exception:
                continue
    return graph


def detect_cycles(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Находит циклы в ориентированном графе зависимостей (если есть).

    Возвращает список циклов, где каждый цикл — список вершин в порядке.
    """
    visited: Set[str] = set()
    stack: List[str] = []
    onstack: Set[str] = set()
    cycles: List[List[str]] = []

    def dfs(v: str):
        visited.add(v)
        stack.append(v)
        onstack.add(v)
        for w in graph.get(v, []):
            if w not in visited:
                dfs(w)
            elif w in onstack:
                # найден цикл: собираем часть стека
                try:
                    idx = stack.index(w)
                    cycle = stack[idx:]
                    cycles.append(cycle.copy())
                except ValueError:
                    pass
        stack.pop()
        onstack.remove(v)

    for node in graph.keys():
        if node not in visited:
            dfs(node)

    # убираем дубликаты циклов (с учётом ротации)
    unique_cycles: List[List[str]] = []
    seen_signatures: Set[Tuple[str, ...]] = set()
    for c in cycles:
        if not c:
            continue
        # нормализуем: сдвинем по наименьшему элементу
        min_idx = min(range(len(c)), key=lambda i: c[i])
        norm = tuple(c[min_idx:] + c[:min_idx])
        if norm not in seen_signatures:
            seen_signatures.add(norm)
            unique_cycles.append(list(norm))
    return unique_cycles


def find_entry_points(py_files: List[Path], root: Path) -> List[str]:
    """Ищет файлы с `if __name__ == "__main__"` или setup-подобные точки входа.

    Возвращает список относительных путей.
    """
    entries: List[str] = []
    for p in py_files:
        try:
            src = p.read_text(encoding='utf-8')
        except Exception:
            continue
        if '__name__' in src and '__main__' in src:
            entries.append(str(p.relative_to(root)))
        elif p.name in ("main.py", "app.py", "run.py"):
            entries.append(str(p.relative_to(root)))
    # уникальность
    return sorted(list(dict.fromkeys(entries)))


def generate_report(root: str, out_file: str = None) -> Dict:
    root_path = Path(root).resolve()
    report = scan_project(str(root_path))
    if out_file is None:
        out_file = root_path / "analyzer_report.json"
    else:
        out_file = Path(out_file)
    try:
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Report written to {out_file}")
    except Exception as e:
        logger.error(f"Failed to write report: {e}")
    return report


# ---- CLI ----
if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser(description='Project Analyzer - scans Python project structure and builds dependency graph')
    ap.add_argument('path', nargs='?', default='.', help='Path to project root')
    ap.add_argument('--out', help='Output JSON file for report')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    root = args.path
    try:
        rep = generate_report(root, args.out)
        # краткий вывод
        print('\nScan summary:')
        print(f"Root: {rep.get('root')}")
        print(f"Python files: {len(rep.get('py_files', []))}")
        print(f"Entry points: {rep.get('entry_points')}")
        cycles = rep.get('cycles', [])
        if cycles:
            print(f"CYCLES FOUND: {len(cycles)}")
            for c in cycles:
                print('  - ' + ' -> '.join(c))
        else:
            print('No cycles detected')
    except Exception as e:
        logger.error(f"Analyzer failed: {e}")
