"""Хук Stop ZCode: напоминает записать в память проекта новую договорённость или урок.

Протокол: вход — JSON события в stdin, выход — JSON с
hookSpecificOutput.additionalContext.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

REMINDER = (
    "[ПАМЯТЬ ПРОЕКТА] Если в этой работе появилась договорённость с заказчиком "
    "или урок, запиши её в memory/agreements/ или memory/lessons/ "
    "по правилам memory/README.md."
)


def main() -> None:
    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else {}
    except ValueError:
        event = {}
    event_name = event.get("hook_event_name") or event.get("hookEventName") or "Stop"
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": REMINDER,
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
