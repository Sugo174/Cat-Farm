"""
Игровые объекты Cat Farm.

Здесь находятся классы, которые можно создать много раз:
коты, частицы награды и будущие предметы фермы.
"""

import math
import random

import pygame


# =============================================================================
# 1. Кот
# =============================================================================

class Cat:
    """Кот, который гуляет по игровой зоне и слегка покачивается при ходьбе."""

    def __init__(
        self,
        x: int,
        y: int,
        color: tuple[int, int, int] | list[int] | None = None,
        name: str = "",
    ):
        self.x = float(x)
        self.y = float(y)
        self.name = name

        self.base_y = float(y)
        self.direction = random.choice([-1, 1])

        self.animation_time = random.uniform(0, math.tau)
        self.speed = random.randint(25, 45)
        self.activity = "walking"
        self.activity_timer = random.uniform(4.0, 8.0)

        self.color = (
            tuple(color)
            if color is not None
            else random.choice(
                [
                    (200, 160, 100),
                    (120, 120, 130),
                    (235, 235, 225),
                    (55, 55, 65),
                    (220, 150, 120),
                ]
            )
        )

    def update(self, delta_time: float, area_width: int):
        """Обновляет движение и периодические остановки кота."""

        self.animation_time += delta_time * 2
        self.activity_timer -= delta_time

        if self.activity_timer <= 0:
            if self.activity == "walking":
                self.activity = "sitting"
                self.activity_timer = random.uniform(2.0, 4.0)
            else:
                self.activity = "walking"
                self.activity_timer = random.uniform(4.0, 8.0)
                self.direction = random.choice([-1, 1])

        if self.activity == "sitting":
            self.y = self.base_y
            return

        self.y = self.base_y + math.sin(self.animation_time) * 3
        self.x += self.direction * self.speed * delta_time

        left_border = 20
        right_border = area_width - 20

        if self.x < left_border:
            self.x = left_border
            self.direction = 1

        if self.x > right_border:
            self.x = right_border
            self.direction = -1

    def draw(
        self,
        surface: pygame.Surface,
        eyes_closed: bool = False,
    ):
        """Рисует временную простую форму кота."""

        x = int(self.x)
        y = int(self.y)

        # Тело.
        pygame.draw.ellipse(
            surface,
            self.color,
            (x - 12, y - 8, 24, 16),
        )

        # Голова.
        pygame.draw.circle(surface, self.color, (x, y - 14), 10)

        # Уши.
        pygame.draw.polygon(
            surface,
            self.color,
            [
                (x - 8, y - 20),
                (x - 3, y - 12),
                (x - 10, y - 14),
            ],
        )
        pygame.draw.polygon(
            surface,
            self.color,
            [
                (x + 8, y - 20),
                (x + 3, y - 12),
                (x + 10, y - 14),
            ],
        )

        # Глаза и рот.
        face_color = (30, 30, 30)

        if eyes_closed:
            pygame.draw.line(
                surface,
                face_color,
                (x - 5, y - 15),
                (x - 1, y - 15),
                2,
            )
            pygame.draw.line(
                surface,
                face_color,
                (x + 1, y - 15),
                (x + 5, y - 15),
                2,
            )
        else:
            pygame.draw.circle(
                surface,
                face_color,
                (x - 3, y - 15),
                2,
            )
            pygame.draw.circle(
                surface,
                face_color,
                (x + 3, y - 15),
                2,
            )

        pygame.draw.arc(
            surface,
            face_color,
            (x - 4, y - 6, 8, 4),
            math.pi,
            0,
            2,
        )
        
    def is_hovered(self, mouse_position: tuple[int, int]) -> bool:
        """Проверяет, находится ли курсор достаточно близко к коту."""

        mouse_x, mouse_y = mouse_position

        return (
            (mouse_x - self.x) ** 2
            + (mouse_y - self.y) ** 2
            <= 26 ** 2
        )

    def draw_name(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ):
        """Рисует имя кота над его головой."""

        if not self.name:
            return

        name_surface = font.render(
            self.name,
            True,
            (245, 245, 245),
        )

        name_rect = name_surface.get_rect(
            center=(
                int(self.x),
                int(self.y - 38),
            ),
        )

        background_rect = name_rect.inflate(12, 6)

        pygame.draw.rect(
            surface,
            (20, 25, 30),
            background_rect,
            border_radius=6,
        )

        surface.blit(name_surface, name_rect)


# =============================================================================
# 2. Частица награды
# =============================================================================

    def is_hovered(self, mouse_position: tuple[int, int]) -> bool:
        """Проверяет, находится ли курсор достаточно близко к коту."""

        mouse_x, mouse_y = mouse_position

        return (
            (mouse_x - self.x) ** 2
            + (mouse_y - self.y) ** 2
            <= 26 ** 2
        )

    def draw_name(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ):
        """Рисует имя кота над его головой."""

        if not self.name:
            return

        name_surface = font.render(
            self.name,
            True,
            (245, 245, 245),
        )

        name_rect = name_surface.get_rect(
            center=(
                int(self.x),
                int(self.y - 38),
            ),
        )

        background_rect = name_rect.inflate(12, 6)

        pygame.draw.rect(
            surface,
            (20, 25, 30),
            background_rect,
            border_radius=6,
        )

        surface.blit(name_surface, name_rect)


class RewardParticle:
    """Короткая анимация текста с полученной наградой."""

    def __init__(self, x: int, y: int, text: str):
        self.x = float(x)
        self.y = float(y)
        self.text = text

        self.life = 1.0

    @property
    def is_alive(self) -> bool:
        """Возвращает True, пока частица должна отображаться."""

        return self.life > 0

    def update(self, delta_time: float):
        """Поднимает частицу и постепенно завершает её жизнь."""

        self.y -= 30 * delta_time
        self.life -= delta_time * 1.5

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Рисует полупрозрачный текст частицы."""

        if not self.is_alive:
            return

        text_surface = font.render(self.text, True, (255, 215, 0))
        text_surface.set_alpha(int(self.life * 255))

        surface.blit(
            text_surface,
            (
                int(self.x - text_surface.get_width() / 2),
                int(self.y),
            ),
        )