# keymapper.py

# --- El encargado de mappear el teclado para su uso en main.py ---

from utils import draw_centered_text, build_responsive_font
import pygame
import json
import os
from config import (
    BINDINGS_PATH,
    get_button_labels,
    get_bindings_format_key
)

# Declara las direcciones

DIRECTIONS = ["Arriba", "Abajo", "Izquierda", "Derecha"]

# Función de mapeo

def map_keys(screen, button_count):
    bindings = {}

    # Avisar si se va a reconfigurar
    formato = get_bindings_format_key(button_count)
    print(f"[INFO] Configurando bindings para: {formato}")

    # Capturar direcciones y botones
    for name in DIRECTIONS + get_button_labels(button_count):
        key = wait_for_keypress(screen, f"Presiona una tecla para: {name}")
        bindings[name] = key

    if os.path.exists(BINDINGS_PATH):
        with open(BINDINGS_PATH, "r") as f:
            all_bindings = json.load(f)
    else:
        all_bindings = {}

    all_bindings[formato] = bindings
    dir_path = os.path.dirname(BINDINGS_PATH)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(BINDINGS_PATH, "w") as f:
        json.dump(all_bindings, f, indent=4)

    return bindings

# encargado de registrar la accion de mapear

def wait_for_keypress(screen, message):
    waiting = True
    while waiting:
        font, line_gap = build_responsive_font(
            screen,
            [message, "Esc para cancelar"],
            base_size=28,
            min_size=14,
            max_size=34,
            base_resolution=(620, 360),
        )
        screen.fill((0, 0, 0))
        title_y = max(32, line_gap)
        draw_centered_text(screen, font, message, y=title_y)
        draw_centered_text(screen, font, "Esc para cancelar", y=title_y + line_gap)
        pygame.display.flip()

        # Manejo de salida matando con ayuda del foco o con Esc, tambien encargado de registrar la tecla para el mapeo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                return event.key

