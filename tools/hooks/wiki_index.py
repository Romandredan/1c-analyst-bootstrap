"""Хук SessionStart ZCode: показывает агенту оглавление wiki проекта.

Протокол: вход — JSON события в stdin, выход — JSON с
hookSpecificOutput.additionalContext. Тексты страниц не загружаются:
агент читает нужные сам по ссылкам из индекса. Если wiki/ нет,
хук завершается молча.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

WIKI_INDEX = Path(__file__).resolve().parents[2] / "wiki" / "index.md"


def pages_of(index_text: str):
    """Строки страниц из индекса: (раздел, строка)."""
    pages = []
    section = ""
    for line in index_text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.lstrip().startswith("- [") and section:
            pages.append((section, line.strip().lstrip("- ").strip()))
    return pages


def build_context() -> str:
    if not WIKI_INDEX.is_file():
        return ""
    pages = pages_of(WIKI_INDEX.read_text(encoding="utf-8"))
    if not pages:
        return (
            "[WIKI ПРОЕКТА] Страниц пока нет. Правила записи: wiki/AGENTS.md. "
            "Разделы не заданы: при первом знании о том, как устроена система "
            "или процесс, предложи владельцу список разделов (4–7) одним списком."
        )
    lines = [
        f"[WIKI ПРОЕКТА] Страниц: {len(pages)}. "
        "Ответ по знаниям начинай с индекса:"
    ]
    for section, page in pages:
        lines.append(f"  {section} · {page}")
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
