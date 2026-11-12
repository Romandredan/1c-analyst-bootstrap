"""Хук Stop: напоминает записать в память проекта новую договорённость или урок."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

print(
    "[ПАМЯТЬ ПРОЕКТА] Если в этой работе появилась договорённость с заказчиком "
    "или урок, запиши её в memory/agreements/ или memory/lessons/ "
    "по правилам memory/README.md."
)
