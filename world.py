"""
Данные игрового мира Cat Farm.

Здесь описывается начальное состояние новой игры и первая локация.
В будущем каждая локация будет хранить свой набор котов, постройки,
декор и прогресс походов.
"""

import secrets
from copy import deepcopy

from cat_factory import generate_location_cat_pool


# =============================================================================
# 1. Общие настройки мира
# =============================================================================

SAVE_VERSION = 2

START_LOCATION_ID = "sunny_meadow"


# =============================================================================
# 2. Создание локаций
# =============================================================================

def create_start_location() -> dict:
    """Создаёт первую локацию игрока — Солнечную поляну."""

    return {
        "id": START_LOCATION_ID,
        "name": "Солнечная поляна",
        "cat_capacity": 10,

        # Идентификаторы котов, которые уже живут на этой локации.
        "resident_cat_ids": [],

        # Список будущих котов для спасения.
        # Он будет сгенерирован один раз и сохранён в JSON.
        "available_cats": [],
        "cat_pool_seed": None,

        # Постройки и декоративные предметы этой локации.
        "buildings": [],
        "decorations": [],

        # Прогресс цепочки походов для освобождения котов.
        "encounter_progress": 0,
    }


def prepare_location_cat_pool(location: dict):
    """
    Создаёт постоянный набор котов для спасения.

    Функция ничего не меняет, если набор уже существует.
    Поэтому коты не будут случайно меняться после перезапуска.
    """

    if location["available_cats"]:
        return

    cat_count = (
        location["cat_capacity"]
        - len(location["resident_cat_ids"])
    )

    location["cat_pool_seed"] = secrets.randbits(32)

    location["available_cats"] = generate_location_cat_pool(
        location_id=location["id"],
        cat_count=cat_count,
        seed=location["cat_pool_seed"],
    )


# =============================================================================
# 3. Создание новой игры
# =============================================================================

def create_new_game_state() -> dict:
    """
    Возвращает полное состояние новой игры.

    Коты пока отсутствуют: первый кот будет добавлен через отдельное
    окно знакомства и выбора имени.
    """

    return {
        "save_version": SAVE_VERSION,

        # Экономика.
        "coins": 0.0,
        "coins_per_key": 1,
        "total_key_presses": 0,

        # Мир и локации.
        "active_location_id": START_LOCATION_ID,
        "locations": [
            create_start_location(),
        ],

        # Все спасённые коты игрока.
        "cats": [],

        # Первый запуск: нужно показать знакомство со стартовым котом.
        "starter_cat_ready": True,
        "starter_cat_preview": None,
    }


def copy_new_game_state() -> dict:
    """Возвращает независимую копию состояния новой игры."""

    return deepcopy(create_new_game_state())