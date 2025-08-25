# main.py

# ---Archivo principal ---

import pygame
import threading
import sys
import os
import config
import json
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG
from button_format_selector import choose_button_format
from input_selector import choose_input_mode
from keymapper import map_keys
from joystick_mapper import map_joystick_buttons
from input_reader import start_input_listener
from hud_renderer import draw_hud, load_icons
from config import get_button_labels
BINDINGS_PATH = "bindings.json"

# Funcines Principales

def main():
    # Inicializar Pygame
    pygame.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Arcade HUD Overlay")
    button_count = choose_button_format(screen)
    input_state = {
        "stick": [0, 0],
        "buttons": [False] * len(get_button_labels(button_count))
    }
    config.BUTTON_FORMAT = button_count
    load_icons(button_count)
    input_mode = choose_input_mode(screen)
    clock = pygame.time.Clock()

    # Selección de modo de entrada (segun que se selecciono)
    if input_mode == "teclado":
        try:
            with open(BINDINGS_PATH, "r") as f:
                data = json.load(f)
                formato = f"formato_{button_count}"
                if formato not in data:
                    print(f"[WARN] No hay bindings para {formato}. Se pedirá configuración.")
                    map_keys(screen, button_count)
        except Exception as e:
            print(f"[ERROR] bindings.json inválido: {e}")
            map_keys(screen, button_count)

    if input_mode == "joystick":
        try:
            with open("joystick_bindings.json", "r") as f:
                all_bindings = json.load(f)
                formato = f"formato_{button_count}"
                if formato not in all_bindings:
                    print(f"[WARN] No hay bindings de joystick para {formato}. Se pedirá configuración.")
                    map_joystick_buttons(screen, button_count) # <--- CORREGIDO
        except Exception as e:
            print(f"[ERROR] joystick_bindings.json inválido o faltante: {e}")
            map_joystick_buttons(screen, button_count) # <--- Y CORREGIDO

    # Iniciar hilo de lectura de entradas
    threading.Thread(
        target=start_input_listener,
        args=(input_mode, button_count, input_state), # Nuevos argumentos
        daemon=True
    ).start()

    # Bucle principal
    running = True
    while running:
        screen.fill((COLOR_BG))  # Fondo "transparente" (Lo puedes cambiar)
        draw_hud(screen, input_state, button_count)
        pygame.display.flip()

        # Manejo de salida matando el proceso con ayuda del foco o con la tecla Esc
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

