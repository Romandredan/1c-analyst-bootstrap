"""Хук SessionStart ZCode: показывает агенту оглавление памяти проекта.

Протокол: вход — JSON события в stdin, выход — JSON с
hookSpecificOutput.additionalContext. Тела записей не загружаются:
агент читает нужные сам по пути из оглавления. Если папки memory/ нет,
хук завершается молча.
"""
import json
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


def build_context() -> str:
    if not MEMORY_DIR.is_dir():
        return ""
    records = sorted(
        p for p in MEMORY_DIR.rglob("*.md") if p.name.lower() != "readme.md"
    )
    if not records:
        return "[ПАМЯТЬ ПРОЕКТА] Записей пока нет. Правила записи: memory/README.md"
    lines = [
        f"[ПАМЯТЬ ПРОЕКТА] Записей: {len(records)}. "
        "Прочитай относящиеся к задаче перед работой:"
    ]
    for path in records:
        rel = path.relative_to(MEMORY_DIR.parent).as_posix()
        desc = description_of(path)
        lines.append(f"  {rel}" + (f" - {desc}" if desc else ""))
    return "\n".join(lines)


def main() -> None:
    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else {}
    except ValueError:
        event = {}
    event_name = (
        event.get("hook_event_name")
        or event.get("hookEventName")
        or "SessionStart"
    )
    context = build_context()
    if not context:
        return
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": context,
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
