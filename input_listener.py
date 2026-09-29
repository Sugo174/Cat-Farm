"""
Безопасный учёт нажатий клавиатуры.

Модуль считает допустимые нажатия и передаёт игре только их количество.
Он не сохраняет введённый текст, имена клавиш или историю действий.
"""

from queue import SimpleQueue

import keyboard


# =============================================================================
# 2. Глобальный слушатель клавиатуры
# =============================================================================

class GlobalKeyListener:
    """
    Слушает клавиатуру в фоновом потоке.

    Важно: обработчик не изменяет игровое состояние напрямую.
    Он складывает количество нажатий в очередь, а игра забирает их
    в своём основном цикле. Это безопаснее для Pygame.
    """

    def __init__(self):
        self.enabled = False

        self._presses = SimpleQueue()
        self._hook = None

    def start(self):
        """Включает глобальное отслеживание нажатий."""

        if self._hook is not None:
            return

        self.enabled = True
        self._hook = keyboard.on_press(
            self._on_key_press,
            suppress=False,
        )

    def stop(self):
        """Отключает отслеживание и освобождает обработчик keyboard."""

        self.enabled = False

        if self._hook is not None:
            keyboard.unhook(self._hook)
            self._hook = None

    def set_enabled(self, enabled: bool):
        """Включает или выключает начисление игровых очков."""

        self.enabled = enabled

    def consume_press_count(self) -> int:
        """
        Возвращает число новых нажатий с прошлого вызова.

        Сами символы нигде не возвращаются и не сохраняются.
        """

        press_count = 0

        while not self._presses.empty():
            self._presses.get()
            press_count += 1

        return press_count

    def _on_key_press(self, event):
        """
        Получает событие от библиотеки keyboard.

        Имя нажатой клавиши нужно только на этот момент, чтобы решить,
        учитывать ли её. В файл, список или игровое сохранение оно
        никогда не записывается.
        """

        if not self.enabled:
            return

        key_name = event.name

        if self._is_counted_key(key_name):
            self._presses.put(1)

    @staticmethod
    def _is_counted_key(key_name: str | None) -> bool:
        """
        Учитывает любую клавишу, которую Windows передала приложению.

        Имя клавиши используется только для проверки текущего события
        и не сохраняется в игровом состоянии или файле.
        """

        return key_name not in {
            None,
            "unknown",
        }