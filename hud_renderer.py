# hud_renderer.py

# --- Encargado de dibujar todo en la ventana ---

import pygame
import os

from config import (
    JOYSTICK_CENTER, JOYSTICK_RADIUS, JOYSTICK_STICK_LENGTH,
    BUTTON_RADIUS, get_icon_paths, get_button_positions,
    COLOR_STICK, COLOR_STICK_KNOB, COLOR_BUTTON_ACTIVE, COLOR_BUTTON_INACTIVE,
    COLOR_TEXT, get_button_labels, get_hud_fallback_text
)

# Carga de íconos al iniciar
icons = []
current_stick_color = COLOR_STICK_KNOB
current_controller_style = "default"

def load_icons(button_count, custom_icon_paths=None):
    global icons
    icons = []
    labels = get_button_labels(button_count)
    default_paths = get_icon_paths(button_count)
    icon_paths = []
    for index, label in enumerate(labels):
        path = default_paths[index]
        if custom_icon_paths and label in custom_icon_paths:
            custom_path = custom_icon_paths[label]
            if custom_path is None:
                icon_paths.append(None)
                continue
            path = custom_path
        icon_paths.append(path)

    for path in icon_paths:
        if path is None:
            icons.append(None)
            continue
        if os.path.exists(path):
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (BUTTON_RADIUS * 2, BUTTON_RADIUS * 2))
            icons.append(image)
        else:
            print(f"[WARN] Ícono no encontrado: {path}")
            icons.append(None)

def set_stick_color(color):
    global current_stick_color
    if isinstance(color, list) and len(color) == 3:
        current_stick_color = tuple(color)
    elif isinstance(color, tuple) and len(color) == 3:
        current_stick_color = color

def set_controller_style(style):
    global current_controller_style
    current_controller_style = style or "default"

# Coloca todo en la ventana 

def draw_hud(screen, state, button_count):
    draw_stick(screen, state["stick"])
    draw_buttons(screen, state["buttons"], button_count)

# Dibuja el stick

def draw_stick(screen, vec):
    center_x, center_y = JOYSTICK_CENTER
    base_radius = JOYSTICK_RADIUS
    stick_length = JOYSTICK_STICK_LENGTH

    dx = vec[0]
    dy = vec[1]

    # Normalizar diagonal y sus limites
    if dx != 0 and dy != 0:
        dx *= 1
        dy *= 1

    end_x = int(center_x + dx * stick_length)
    end_y = int(center_y + dy * stick_length)

    # Base
    pygame.draw.circle(screen, (100, 100, 100), (center_x, center_y), base_radius)

    # Palanca
    pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (end_x, end_y), 6)
    pygame.draw.circle(screen, current_stick_color, (end_x, end_y), 12)

    # Dibuja los botones

def draw_buttons(screen, button_states, button_count):
    positions = get_button_positions(button_count)
    labels = get_button_labels(button_count)
    label_font = pygame.font.SysFont(None, 18)

    for i, pos in enumerate(positions):
        icon = icons[i]
        pressed = button_states[i]

        if icon:
            rect = icon.get_rect(center=pos)
            screen.blit(icon, rect)
            if pressed:
                pygame.draw.circle(screen, COLOR_BUTTON_ACTIVE, pos, BUTTON_RADIUS, 3)
        else:
            color = COLOR_BUTTON_ACTIVE if pressed else COLOR_BUTTON_INACTIVE
            pygame.draw.circle(screen, color, pos, BUTTON_RADIUS)
            label = get_hud_fallback_text(labels[i], current_controller_style)
            label_surface = label_font.render(label, True, COLOR_TEXT)
            label_rect = label_surface.get_rect(center=pos)
            screen.blit(label_surface, label_rect)

