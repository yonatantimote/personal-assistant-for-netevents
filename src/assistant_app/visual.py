# visual.py

import pygame
import math
from .config import WIDTH, CENTER_Y, HEIGHT


def draw_wave(surface, volume, t):
    points = []

    margin_x = WIDTH * 0.1
    usable_width = WIDTH - 2 * margin_x

    max_amplitude = HEIGHT * 0.25

    for i in range(int(usable_width)):
        # Normalizamos entre -1 y 1 (CLAVE para simetría)
        norm_x = (i / usable_width) * 2 - 1

        # Envolvente simétrica (tipo campana)
        envelope = math.exp(-4 * norm_x**2)

        # Varias frecuencias para hacerlo más orgánico
        wave = (
            math.sin(6 * norm_x + t * 3) +
            0.5 * math.sin(12 * norm_x - t * 2)
        )

        y = CENTER_Y + wave * envelope * volume * max_amplitude

        x = margin_x + i
        points.append((x, y))

    # Dibujar glow (capas grandes primero)
    for glow in range(6, 0, -1):
        alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        color = (0, 200, 255, 30)
        pygame.draw.aalines(alpha_surface, color, False, points, glow)
        surface.blit(alpha_surface, (0, 0))

    # Línea principal
    pygame.draw.aalines(surface, (0, 255, 200), False, points, 2)



def draw_wave_layer(surface, volume, t, color, offset):
    points = []
    margin_x = WIDTH * 0.1
    usable_width = WIDTH - 2 * margin_x
    max_amplitude = HEIGHT * 0.25

    for i in range(int(usable_width)):
        norm_x = (i / usable_width) * 2 - 1
        envelope = math.exp(-4 * norm_x**2)

        wave = (
            math.sin(6 * norm_x + t * 3 + offset) +
            0.5 * math.sin(12 * norm_x - t * 2)
        )

        y = CENTER_Y + wave * envelope * volume * max_amplitude
        x = margin_x + i
        points.append((x, y))

    pygame.draw.aalines(surface, color, False, points, 2)