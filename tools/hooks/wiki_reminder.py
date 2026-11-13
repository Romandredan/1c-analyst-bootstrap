"""Хук Stop ZCode: напоминает записать в wiki механику, выясненную в работе.

Протокол: вход — JSON события в stdin, выход — JSON с
hookSpecificOutput.additionalContext. Условный: срабатывает, только когда
в docs/adr/, docs/research/ или memory/ есть файлы новее последней записи
в wiki/log.md. Иначе молчит.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
WIKI_LOG = ROOT / "wiki" / "log.md"
WATCHED_DIRS = ("docs/adr", "docs/research", "memory")
MAX_LISTED = 10


def fresh_sources():
    """Файлы наблюдаемых папок новее wiki/log.md: (путь, время изменения)."""
    try:
        last_wiki = WIKI_LOG.stat().st_mtime
    except OSError:
        last_wiki = 0.0
    fresh = []
    for name in WATCHED_DIRS:
        folder = ROOT / name
        if not folder.is_dir():
            continue
        for path in folder.rglob("*.md"):
            if path.name.lower() == "readme.md":
                continue
            mtime = path.stat().st_mtime
            if mtime > last_wiki:
                fresh.append((path, mtime))
    return sorted(fresh, key=lambda item: item[1], reverse=True)


def build_context() -> str:
    fresh = fresh_sources()
    if not fresh:
        return ""
    lines = ["[WIKI ПРОЕКТА] Есть материалы новее последней записи в wiki/log.md:"]
    for path, mtime in fresh[:MAX_LISTED]:
        when = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {path.relative_to(ROOT).as_posix()} ({when})")
    if len(fresh) > MAX_LISTED:
        lines.append(f"  … и ещё {len(fresh) - MAX_LISTED}")
    lines.append(
        "Если из них выяснена механика «как устроено» (проверка кода, ответ "
        "адресата) — запиши её страницей wiki по правилам wiki/AGENTS.md; "
        "такой страницы ещё нет — создай тем же действием, что и ADR. "
        "Нечего записать — пропусти напоминание."
    )
    return "\n".join(lines)


def main() -> None:
    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else {}
    except ValueError:
        event = {}
    event_name = event.get("hook_event_name") or event.get("hookEventName") or "Stop"
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
