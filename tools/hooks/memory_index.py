"""Хук SessionStart: показывает агенту оглавление памяти проекта.

Тела записей не загружаются: агент читает нужные сам по пути из оглавления.
Если папки memory/ нет, хук молча завершается.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

MEMORY_DIR = Path(__file__).resolve().parents[2] / "memory"


def description_of(path: Path) -> str:
    """Строка description из шапки записи, если она есть."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""


def main() -> None:
    if not MEMORY_DIR.is_dir():
        return
    records = sorted(
        p for p in MEMORY_DIR.rglob("*.md") if p.name.lower() != "readme.md"
    )
    if not records:
        print("[ПАМЯТЬ ПРОЕКТА] Записей пока нет. Правила записи: memory/README.md")
        return
    print(f"[ПАМЯТЬ ПРОЕКТА] Записей: {len(records)}. Прочитай относящиеся к задаче:")
    for path in records:
        rel = path.relative_to(MEMORY_DIR.parent).as_posix()
        desc = description_of(path)
        print(f"  {rel}" + (f" - {desc}" if desc else ""))


if __name__ == "__main__":
    main()
