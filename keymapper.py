# keymapper.py

# --- El encargado de mappear el teclado para su uso en main.py ---

from utils import draw_centered_text
import pygame
import json
import os
from config import (
    BINDINGS_PATH,
    COLOR_TEXT,
    SCREEN_WIDTH,
    get_button_labels
)

# Declara las direcciones

DIRECTIONS = ["Arriba", "Abajo", "Izquierda", "Derecha"]

# Función de mapeo

def map_keys(screen, button_count):
    font = pygame.font.SysFont(None, 28)
    bindings = {}

    # Avisar si se va a reconfigurar
    formato = f"formato_{len(get_button_labels(button_count))}"
    print(f"[INFO] Configurando bindings para: {formato}")

    # Capturar direcciones y botones
    for name in DIRECTIONS + get_button_labels(button_count):
        key = wait_for_keypress(screen, font, f"Presiona una tecla para: {name}")
        bindings[name] = key

    formato = f"formato_{len(get_button_labels(button_count))}"

    if os.path.exists(BINDINGS_PATH):
        with open(BINDINGS_PATH, "r") as f:
            all_bindings = json.load(f)
    else:
        all_bindings = {}

    all_bindings[formato] = bindings

    with open(BINDINGS_PATH, "w") as f:
        json.dump(all_bindings, f, indent=4)

# encargado de registrar la accion de mapear

def wait_for_keypress(screen, font, message):
    waiting = True
    while waiting:
        screen.fill((0, 0, 0))
        draw_centered_text(screen, font, message, y=75)
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
            elif event.type == pygame.KEYDOWN:
                return event.key
