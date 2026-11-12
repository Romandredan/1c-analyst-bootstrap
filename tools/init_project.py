"""Заполнить шаблон проекта аналитика или наложить его на другой репозиторий.

Два режима:

    python tools/init_project.py --name "VIP-примерка" [--system "Управление торговлей 11.5"] [--code-alias ut]
        Заполняет места шаблона в этом репозитории. Режим для проекта,
        созданного из шаблона кнопкой «Use this template» или командой git clone.

    python tools/init_project.py --into D:/work/team-repo --name "VIP-примерка" [...]
        Копирует структуру шаблона в другую папку, например в репозиторий команды
        разработки. Существующие файлы не перезаписываются и перечисляются в
        отчёте; места заполняются только в скопированных файлах.

После запуска скрипт перечисляет места, которые остались незаполненными: их
вписывает человек или агент.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ""}
# Файлы самого шаблона: в проект при наложении не копируются и не заполняются.
TEMPLATE_ONLY = {"LICENSE", "CHANGELOG.md", "tools/init_project.py"}
SKIP_PARTS = {".git", "__pycache__"}
README_TITLE = "# Проект аналитика 1С"
PLACE_RE = re.compile(r"<[А-ЯЁ][^<>\n]*>")


def template_files() -> list[Path]:
    files = []
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file() or SKIP_PARTS.intersection(rel.parts):
            continue
        if rel.as_posix() in TEMPLATE_ONLY:
            continue
        files.append(path)
    return files


def is_text(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES and path.name != ".gitkeep"


def fill(text: str, values: dict[str, str], name: str) -> str:
    for placeholder, value in values.items():
        text = text.replace(placeholder, value)
    lines = text.split("\n")
    if lines and lines[0].strip() == README_TITLE:
        lines[0] = f"# {name}"
    return "\n".join(lines)


def places_left(paths: list[Path], base: Path) -> list[str]:
    left = []
    for path in paths:
        if not path.is_file() or not is_text(path):
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for match in PLACE_RE.findall(line):
                left.append(f"{path.relative_to(base).as_posix()}:{number}: {match}")
    return left


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Заполнить или наложить шаблон проекта аналитика")
    parser.add_argument("--name", required=True, help="имя проекта")
    parser.add_argument("--system", help="система, например «Управление торговлей 11.5»")
    parser.add_argument("--code-alias", help="алиас конфигурации в индексе code-index")
    parser.add_argument("--into", type=Path, help="папка, на которую наложить шаблон; без неё заполняется этот репозиторий")
    args = parser.parse_args()

    values = {"<ПРОЕКТ>": args.name}
    if args.system:
        values["<СИСТЕМА>"] = args.system
    if args.code_alias:
        values["<АЛИАС_КОДА>"] = args.code_alias

    touched: list[Path] = []
    if args.into is None:
        base = ROOT
        for path in template_files():
            if is_text(path):
                text = path.read_text(encoding="utf-8")
                new = fill(text, values, args.name)
                if new != text:
                    path.write_text(new, encoding="utf-8")
                    touched.append(path)
        print(f"Проект: {base}")
        print(f"Заполнено файлов: {len(touched)}")
        checked = template_files()
    else:
        base = args.into.resolve()
        if base == ROOT:
            print("ОШИБКА: --into указывает на сам шаблон; для заполнения запустите без --into")
            return 1
        skipped = []
        for source in template_files():
            rel = source.relative_to(ROOT)
            dest = base / rel
            if dest.exists():
                skipped.append(rel.as_posix())
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            if is_text(source):
                dest.write_text(fill(source.read_text(encoding="utf-8"), values, args.name), encoding="utf-8")
            else:
                shutil.copy2(source, dest)
            touched.append(dest)
        print(f"Проект: {base}")
        print(f"Скопировано файлов: {len(touched)}")
        if skipped:
            print(f"Пропущено, файл уже есть ({len(skipped)}):")
            for rel in skipped:
                print(f"  {rel}")
        checked = touched

    left = places_left(checked, base)
    if left:
        print(f"Осталось заполнить ({len(left)}):")
        for item in left:
            print(f"  {item}")
    else:
        print("Незаполненных мест нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
