"""Smoke pytest: menú principal sale con ESC sin intervención manual."""

import os
import sys
import threading
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ROOT)
sys.path.insert(0, ENGINE)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


@pytest.fixture
def main_app():
	import main as main_app_module

	return main_app_module


def test_run_main_menu_until_action_escape_returns_salir(main_app):
	import pygame
	from config import SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_CAPTION_APP

	pygame.init()
	try:
		screen = main_app._set_window_size(
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			f"{WINDOW_CAPTION_APP} — smoke menú",
		)

		def post_escape():
			time.sleep(2.0)
			pygame.event.post(
				pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
			)

		threading.Thread(target=post_escape, daemon=True).start()
		action = main_app.run_main_menu_until_action(screen)
		assert action == "salir"
	finally:
		pygame.quit()
