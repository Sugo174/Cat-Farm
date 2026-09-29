"""
Основной игровой цикл Cat Farm.

Модуль объединяет окно Pygame, игровой мир, котов,
сохранение и знакомство с первым котом.
"""

import random
import time

import pygame

from cat_factory import create_starter_cat
from config import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    FPS,
    MAIN_TEXT_COLOR,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from entities import Cat, RewardParticle
from input_listener import GlobalKeyListener
from onboarding import StarterCatDialog
from save_manager import load_game_state, save_game_state
from world import prepare_location_cat_pool


# =============================================================================
# 1. Вспомогательные функции
# =============================================================================

def format_number(value: float) -> str:
    """Красиво сокращает большие значения: 1250 превращается в 1.2k."""

    if value >= 1000:
        return f"{value / 1000:.1f}k"

    return str(int(value))


def draw_rounded_rect(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    rectangle: pygame.Rect,
    radius: int = 8,
):
    """Рисует прямоугольник со скруглёнными углами."""

    pygame.draw.rect(
        surface,
        color,
        rectangle,
        border_radius=radius,
    )


# =============================================================================
# 2. Основной класс игры
# =============================================================================

class CatFarmGame:
    """Хранит игровое состояние и управляет главным циклом Pygame."""

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.SysFont("consolas", 14)
        self.font_normal = pygame.font.SysFont("consolas", 16)
        self.font_title = pygame.font.SysFont(
            "consolas",
            20,
            bold=True,
        )

        # Загружаем мир, монеты, локации и список спасённых котов.
        self.state = load_game_state()

        self.coins = float(self.state["coins"])
        self.coins_per_key = int(self.state["coins_per_key"])
        self.total_key_presses = int(
            self.state["total_key_presses"],
        )

        self.active_location = self._get_active_location()

        self.cats: list[Cat] = []
        self.particles: list[RewardParticle] = []

        for cat_data in self.state["cats"]:
            self._create_cat_visual(cat_data)

        self.key_listener = GlobalKeyListener()
        self.tracking_error = None

        try:
            self.key_listener.start()
        except Exception as error:
            self.tracking_error = str(error)

        self.starter_dialog = None

        if self.state["starter_cat_ready"]:
            self._start_starter_onboarding()

        self.last_save_time = time.time()
        self.running = True

    def run(self):
        """Запускает игру и выполняет цикл до закрытия окна."""

        while self.running:
            delta_time = self.clock.tick(FPS) / 1000

            self._handle_pygame_events()
            self._process_keyboard_presses()
            self._update(delta_time)
            self._draw()

        self._shutdown()

    def _get_active_location(self) -> dict:
        """Возвращает локацию, которая сейчас открыта у игрока."""

        active_location_id = self.state["active_location_id"]

        for location in self.state["locations"]:
            if location["id"] == active_location_id:
                return location

        return self.state["locations"][0]

    def _start_starter_onboarding(self):
        """Открывает окно знакомства с первым котом."""

        preview_cat = self.state["starter_cat_preview"]

        if preview_cat is None:
            preview_cat = create_starter_cat(name="")

            self.state["starter_cat_preview"] = preview_cat
            self._save_progress()

        self.starter_dialog = StarterCatDialog(preview_cat)

        # Имя кота не должно приносить игроку монеты.
        self.key_listener.set_enabled(False)

        pygame.key.start_text_input()

    def _finish_starter_onboarding(self, cat_data: dict):
        """Добавляет названного кота на ферму и закрывает окно знакомства."""

        cat_data["origin_location_id"] = self.active_location["id"]
        cat_data["current_location_id"] = self.active_location["id"]

        self.state["cats"].append(cat_data)

        self.active_location["resident_cat_ids"].append(
            cat_data["id"],
        )

        prepare_location_cat_pool(self.active_location)

        self.state["starter_cat_ready"] = False
        self.state["starter_cat_preview"] = None

        self._create_cat_visual(cat_data)

        self.starter_dialog = None

        pygame.key.stop_text_input()

        self.key_listener.set_enabled(True)
        self._save_progress()

    def _create_cat_visual(self, cat_data: dict):
        """Создаёт отображаемого кота из сохранённых игровых данных."""

        if (
            cat_data["current_location_id"]
            != self.active_location["id"]
        ):
            return

        self.cats.append(
            Cat(
                x=random.randint(40, WINDOW_WIDTH - 40),
                y=random.randint(300, 370),
                color=cat_data["color"],
                name=cat_data["name"],
            )
        )

    def _handle_pygame_events(self):
        """Обрабатывает системные события окна и окно знакомства."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self.starter_dialog is not None:
                adopted_cat = self.starter_dialog.handle_event(event)

                if adopted_cat is not None:
                    self._finish_starter_onboarding(adopted_cat)

                continue

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                self.running = False

    def _process_keyboard_presses(self):
        """Превращает новые нажатия в игровые монеты."""

        press_count = self.key_listener.consume_press_count()

        if press_count == 0:
            return

        reward = press_count * self.coins_per_key

        self.coins += reward
        self.total_key_presses += press_count

        self.particles.append(
            RewardParticle(
                x=random.randint(100, WINDOW_WIDTH - 100),
                y=100,
                text=f"+{format_number(reward)}",
            ),
        )

    def _update(self, delta_time: float):
        """Обновляет котов, частицы и периодически сохраняет игру."""

        for cat in self.cats:
            cat.update(
                delta_time=delta_time,
                area_width=WINDOW_WIDTH,
            )

        for particle in self.particles:
            particle.update(delta_time)

        self.particles = [
            particle
            for particle in self.particles
            if particle.is_alive
        ]

        if time.time() - self.last_save_time >= 10:
            self._save_progress()

    def _draw(self):
        """Рисует текущий кадр игры."""

        self.screen.fill(BACKGROUND_COLOR)

        self._draw_header()
        self._draw_farm()
        self._draw_hint()

        if self.starter_dialog is not None:
            self.starter_dialog.update(
                delta_time=self.clock.get_time() / 1000,
            )
            self.starter_dialog.draw(
                surface=self.screen,
                title_font=self.font_title,
                normal_font=self.font_normal,
                small_font=self.font_small,
            )

        pygame.display.flip()

    def _draw_header(self):
        """Рисует верхнюю панель с монетами и прогрессом локации."""

        panel = pygame.Rect(
            10,
            10,
            WINDOW_WIDTH - 20,
            54,
        )
        draw_rounded_rect(
            self.screen,
            PANEL_COLOR,
            panel,
        )

        coins_text = self.font_title.render(
            f"🐾 {format_number(self.coins)}",
            True,
            ACCENT_COLOR,
        )
        self.screen.blit(coins_text, (24, 25))

        gain_text = self.font_normal.render(
            f"+{self.coins_per_key} за нажатие",
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(gain_text, (190, 29))

        cat_count = len(
            self.active_location["resident_cat_ids"],
        )
        cat_capacity = self.active_location["cat_capacity"]

        cats_text = self.font_normal.render(
            f"🐱 {cat_count}/{cat_capacity}",
            True,
            MAIN_TEXT_COLOR,
        )
        self.screen.blit(cats_text, (470, 29))

    def _draw_farm(self):
        """Рисует первую игровую локацию и живущих на ней котов."""

        location_name = self.font_title.render(
            self.active_location["name"],
            True,
            MAIN_TEXT_COLOR,
        )
        self.screen.blit(location_name, (20, 92))

        description_text = self.font_small.render(
            "Печатай, развивай ферму и спасай новых котов.",
            True,
            MUTED_TEXT_COLOR,
        )

        waiting_cats = sum(
            not cat["is_rescued"]
            for cat in self.active_location["available_cats"]
        )

        rescue_text = self.font_small.render(
            f"Котов ждут спасения: {waiting_cats}",
            True,
            (190, 210, 195),
        )
        self.screen.blit(rescue_text, (20, 143))

        self.screen.blit(description_text, (20, 120))

        grass = pygame.Rect(
            15,
            180,
            WINDOW_WIDTH - 30,
            230,
        )
        draw_rounded_rect(
            self.screen,
            (29, 58, 48),
            grass,
            radius=14,
        )

        hovered_cat = None
        mouse_position = pygame.mouse.get_pos()

        hovered_cat = None
        mouse_position = pygame.mouse.get_pos()

        for cat in self.cats:
            cat.draw(self.screen)

            if cat.is_hovered(mouse_position):
                hovered_cat = cat

        if hovered_cat is not None:
            hovered_cat.draw_name(
                surface=self.screen,
                font=self.font_small,
            )

            if cat.is_hovered(mouse_position):
                hovered_cat = cat

        if hovered_cat is not None:
            hovered_cat.draw_name(
                surface=self.screen,
                font=self.font_small,
            )

        for particle in self.particles:
            particle.draw(
                surface=self.screen,
                font=self.font_normal,
            )

    def _draw_hint(self):
        """Рисует подсказку управления и сообщение об ошибке."""

        if self.tracking_error is not None:
            error_text = self.font_small.render(
                "Не удалось включить учёт клавиатуры.",
                True,
                (230, 120, 120),
            )
            self.screen.blit(error_text, (20, WINDOW_HEIGHT - 52))

        hint_text = self.font_small.render(
            "Esc — выход",
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            hint_text,
            (20, WINDOW_HEIGHT - 28),
        )

    def _save_progress(self):
        """Записывает в словарь текущие монеты и статистику."""

        self.state["coins"] = self.coins
        self.state["coins_per_key"] = self.coins_per_key
        self.state["total_key_presses"] = self.total_key_presses

        save_game_state(self.state)

        self.last_save_time = time.time()

    def _shutdown(self):
        """Сохраняет прогресс и корректно закрывает игру."""

        pygame.key.stop_text_input()

        self._save_progress()

        self.key_listener.stop()
        pygame.quit()