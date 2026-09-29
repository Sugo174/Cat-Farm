"""
Окно знакомства с первым котом.

Игрок получает стартового кота, выбирает ему имя и подтверждает,
что кот будет жить на первой локации.
"""

import pygame

from entities import Cat


# =============================================================================
# 1. Окно знакомства
# =============================================================================

class StarterCatDialog:
    """Модальное окно для первого бесплатного кота."""

    def __init__(self, cat_data: dict):
        self.cat_data = cat_data

        self.name_input = ""
        self.animation_time = 0.0

        self.dialog_rect = pygame.Rect(90, 80, 440, 390)
        self.name_input_rect = pygame.Rect(145, 335, 330, 42)
        self.confirm_button_rect = pygame.Rect(145, 395, 330, 46)

        self.preview_cat = Cat(
            x=310,
            y=250,
            color=cat_data["color"],
        )
        self.preview_cat.speed = 0

    def update(self, delta_time: float):
        """Обновляет лёгкую анимацию кота в окне знакомства."""

        self.animation_time += delta_time

        self.preview_cat.update(
            delta_time=delta_time,
            area_width=620,
        )

    def handle_event(self, event: pygame.event.Event) -> dict | None:
        """
        Обрабатывает ввод имени и нажатие кнопки.

        Возвращает данные кота только после успешного подтверждения.
        """

        if event.type == pygame.TEXTINPUT:
            if len(self.name_input) < 20:
                self.name_input += event.text

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]

            if event.key == pygame.K_RETURN:
                return self._confirm_cat()

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.confirm_button_rect.collidepoint(event.pos)
        ):
            return self._confirm_cat()

        return None

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        normal_font: pygame.font.Font,
        small_font: pygame.font.Font,
    ):
        """Рисует затемнение, карточку кота и поле имени."""

        overlay = pygame.Surface(
            surface.get_size(),
            pygame.SRCALPHA,
        )
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(
            surface,
            (30, 38, 48),
            self.dialog_rect,
            border_radius=16,
        )

        pygame.draw.rect(
            surface,
            (95, 120, 145),
            self.dialog_rect,
            width=2,
            border_radius=16,
        )

        title = title_font.render(
            "Первый котёнок на ферме!",
            True,
            (235, 240, 245),
        )
        surface.blit(
            title,
            (
                self.dialog_rect.centerx - title.get_width() // 2,
                105,
            ),
        )

        description = small_font.render(
            "Дай имя своему новому другу.",
            True,
            (175, 185, 195),
        )
        surface.blit(
            description,
            (
                self.dialog_rect.centerx - description.get_width() // 2,
                138,
            ),
        )

        is_blinking = self.animation_time % 4.0 < 0.15

        self.preview_cat.draw(
            surface,
            eyes_closed=is_blinking,
        )

        coat_text = normal_font.render(
            f"Окрас: {self.cat_data['coat_title']}",
            True,
            (220, 225, 230),
        )
        surface.blit(
            coat_text,
            (
                self.dialog_rect.centerx - coat_text.get_width() // 2,
                280,
            ),
        )

        personality_text = small_font.render(
            f"Характер: {self.cat_data['personality']}",
            True,
            (175, 185, 195),
        )
        surface.blit(
            personality_text,
            (
                self.dialog_rect.centerx
                - personality_text.get_width() // 2,
                305,
            ),
        )

        pygame.draw.rect(
            surface,
            (45, 55, 65),
            self.name_input_rect,
            border_radius=8,
        )

        name_text = self.name_input or "Введи имя кота"

        input_color = (
            (235, 240, 245)
            if self.name_input
            else (140, 150, 160)
        )

        rendered_name = normal_font.render(
            name_text,
            True,
            input_color,
        )
        surface.blit(
            rendered_name,
            (
                self.name_input_rect.x + 12,
                self.name_input_rect.y + 11,
            ),
        )

        can_confirm = bool(self.name_input.strip())

        button_color = (
            (35, 134, 54)
            if can_confirm
            else (65, 70, 75)
        )

        pygame.draw.rect(
            surface,
            button_color,
            self.confirm_button_rect,
            border_radius=8,
        )

        button_text = normal_font.render(
            "Принять на ферму",
            True,
            (255, 255, 255),
        )
        surface.blit(
            button_text,
            (
                self.confirm_button_rect.centerx
                - button_text.get_width() // 2,
                self.confirm_button_rect.y + 13,
            ),
        )

    def _confirm_cat(self) -> dict | None:
        """Проверяет имя и возвращает готовые данные первого кота."""

        name = self.name_input.strip()

        if not name:
            return None

        self.cat_data["name"] = name

        return self.cat_data