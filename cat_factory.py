"""
Создание игровых котов Cat Farm.

Модуль формирует данные котов: внешний вид, характер и стартовые
характеристики. Он не рисует котов на экране — за это отвечает entities.py.
"""

import random
from uuid import uuid4


# =============================================================================
# 1. Варианты внешнего вида и характера
# =============================================================================

CAT_COATS = [
    {
        "id": "ginger",
        "title": "рыжий",
        "color": (220, 145, 80),
    },
    {
        "id": "gray",
        "title": "серый",
        "color": (125, 130, 140),
    },
    {
        "id": "white",
        "title": "белый",
        "color": (235, 235, 225),
    },
    {
        "id": "black",
        "title": "чёрный",
        "color": (55, 55, 65),
    },
    {
        "id": "calico",
        "title": "трёхцветный",
        "color": (210, 155, 125),
    },
]

CAT_PERSONALITIES = [
    "любопытный",
    "спокойный",
    "смелый",
    "сонный",
    "игривый",
    "задумчивый",
]


# =============================================================================
# 2. Стартовые характеристики
# =============================================================================

AVERAGE_STATS = {
    "courage": 5,
    "agility": 5,
    "cleverness": 5,
    "kindness": 5,
}


# =============================================================================
# 3. Создание котов
# =============================================================================

def create_starter_cat(name: str) -> dict:
    """
    Создаёт первого бесплатного кота.

    Все его характеристики специально равны средним значениям.
    Имя вводится игроком во время знакомства с котом.
    """

    random_generator = random.Random()

    coat = random_generator.choice(CAT_COATS)
    personality = random_generator.choice(CAT_PERSONALITIES)

    return {
        "id": uuid4().hex,
        "name": name.strip(),

        "coat_id": coat["id"],
        "coat_title": coat["title"],
        "color": coat["color"],

        "personality": personality,
        "level": 1,
        "experience": 0,

        "stats": AVERAGE_STATS.copy(),

        "origin_location_id": "sunny_meadow",
        "current_location_id": "sunny_meadow",
    }


def generate_location_cat_pool(
    location_id: str,
    cat_count: int,
    seed: int,
) -> list[dict]:
    """
    Генерирует постоянный набор котов для одной локации.

    seed позволяет получить предсказуемый набор. Позже этот список
    сохранится в JSON, поэтому он не будет меняться после перезапуска.
    """

    random_generator = random.Random(seed)
    cat_pool = []

    for number in range(1, cat_count + 1):
        coat = random_generator.choice(CAT_COATS)
        personality = random_generator.choice(CAT_PERSONALITIES)

        cat_pool.append(
            {
                "id": f"{location_id}_rescue_{number}",
                "coat_id": coat["id"],
                "coat_title": coat["title"],
                "color": coat["color"],
                "personality": personality,

                "level": 1,
                "stats": AVERAGE_STATS.copy(),

                "is_rescued": False,
            }
        )

    return cat_pool