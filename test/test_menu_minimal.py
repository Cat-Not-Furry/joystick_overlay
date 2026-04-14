#!/usr/bin/env python3
"""
Reproducción mínima del menú principal.
Aísla show_main_menu para diagnosticar parpadeo.
Si parpadea: problema en menú o entorno (SDL/WM).
Si no parpadea: problema en flujo de ventanas secundarias (config, etc.).

Uso: python test/test_menu_minimal.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

def main():
	import pygame
	import main as main_app
	from config import SCREEN_WIDTH, SCREEN_HEIGHT

	pygame.init()
	os.environ.setdefault("SDL_VIDEO_WINDOW_POS", "100,100")
	screen = main_app._set_window_size(
		SCREEN_WIDTH,
		SCREEN_HEIGHT,
		"Arcade HUD Overlay - Test Mínimo"
	)
	action = main_app.show_main_menu(screen)
	print(f"Acción: {action}")
	pygame.quit()


if __name__ == "__main__":
	main()
