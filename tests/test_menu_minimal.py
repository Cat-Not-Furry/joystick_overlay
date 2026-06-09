#!/usr/bin/env python3
"""
Reproducción mínima del menú principal.
Aísla run_main_menu_until_action para diagnosticar parpadeo.
Si parpadea: problema en menú o entorno (SDL/WM).
Si no parpadea: problema en flujo de ventanas secundarias (config, etc.).

Uso: python tests/test_menu_minimal.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
# Raíz: resolver `main` (main.py). Engine: paquetes config, render, maps, etc.
sys.path.insert(0, ROOT)
sys.path.insert(0, ENGINE)

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_CAPTION_APP


def main():
	import pygame
	import main as main_app

	pygame.init()
	os.environ.setdefault("SDL_VIDEO_WINDOW_POS", "100,100")
	screen = main_app._set_window_size(
		SCREEN_WIDTH,
		SCREEN_HEIGHT,
		f"{WINDOW_CAPTION_APP} — Test mínimo",
	)
	action = main_app.run_main_menu_until_action(screen)
	print(f"Acción: {action}")
	pygame.quit()


if __name__ == "__main__":
	main()
