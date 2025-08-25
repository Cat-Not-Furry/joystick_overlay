# joystick_mapper.py

# --- Encargado de mapear el joystick si se escogio en el selector

import pygame
import json
import evdev
import select
from evdev import InputDevice, ecodes, util
from config import get_button_labels, COLOR_TEXT, SCREEN_WIDTH
from utils import draw_centered_text, show_error_and_exit 

JOYSTICK_BINDINGS_PATH = "joystick_bindings.json"

def map_joystick_buttons(screen, button_count):
    font = pygame.font.SysFont(None, 32)
    labels = get_button_labels(button_count)  # ✅ Solo LP, LK, HP, HK si formato_4

    # Buscar primer joystick disponible (en un futuro se mejorara a un menu seleccionable)
    dev = None
    for path in evdev.list_devices():
        d = InputDevice(path)
        if "joystick" in d.name.lower() or "gamepad" in d.name.lower():
            dev = d
            dev.grab()
            break
    # Si no detecta alguno o se quita mientras se ejecuta el programa
    if not dev:
        show_error_and_exit(screen, "¡Error!\nNo se encontró ningún joystick.")

    print(f"[INFO] Usando joystick: {dev.name}")

    bindings = {}

    for label in labels:
        prompt = f"Presiona el botón para: {label}"
        waiting = True
        while waiting:
            screen.fill((0, 0, 0))
            draw_centered_text(screen, font, prompt, y=75)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

            r, _, _ = select.select([dev], [], [], 0.01)
            if dev in r:
                for event in dev.read():
                    if event.type == ecodes.EV_KEY and event.value == 1:
                        bindings[label] = event.code
                        print(f"[OK] {label} → code {event.code}")
                        waiting = False
                        break

    # Guardar en archivo por formato
    formato = f"formato_{len(get_button_labels(button_count))}"

    try:
        with open(JOYSTICK_BINDINGS_PATH, "r") as f:
            all_bindings = json.load(f)
    except:
        all_bindings = {}

    all_bindings[formato] = bindings

    with open(JOYSTICK_BINDINGS_PATH, "w") as f:
        json.dump(all_bindings, f, indent=4)

    print(f"[OK] Mapeo de joystick guardado en '{JOYSTICK_BINDINGS_PATH}'")
    dev.ungrab()

def draw_centered_text(screen, font, text, y):
    surface = font.render(text, True, COLOR_TEXT)
    rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surface, rect)

