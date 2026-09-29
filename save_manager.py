"""
Загрузка и сохранение игрового прогресса Cat Farm.
"""

import json

from config import SAVE_FILE
from world import SAVE_VERSION, copy_new_game_state


# =============================================================================
# 1. Работа с файлом сохранения
# =============================================================================

def load_game_state() -> dict:
    """
    Загружает сохранение текущей версии или создаёт новую игру.

    Старые файлы сохранения не удаляются и не перезаписываются.
    """

    new_state = copy_new_game_state()

    if not SAVE_FILE.exists():
        return new_state

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as save_file:
            saved_state = json.load(save_file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return new_state

    if not isinstance(saved_state, dict):
        return new_state

    if saved_state.get("save_version") != SAVE_VERSION:
        return new_state

    return saved_state


def save_game_state(state: dict):
    """Сохраняет текущее состояние игры в JSON-файл."""

    with SAVE_FILE.open("w", encoding="utf-8") as save_file:
        json.dump(
            state,
            save_file,
            ensure_ascii=False,
            indent=2,
        )