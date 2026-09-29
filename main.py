"""
Точка входа Cat Farm.

Этот файл намеренно короткий: он только создаёт игру и запускает её.
"""

from game import CatFarmGame


def main():
    """Создаёт и запускает экземпляр игры."""

    game = CatFarmGame()
    game.run()


if __name__ == "__main__":
    main()