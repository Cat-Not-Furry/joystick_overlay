# button_format_selector.py

# --- Encargado de gestionar que formato va a utilizar ---

import pygame
from utils import draw_centered_text, build_responsive_font

KEY_TO_VALUE = {pygame.K_4: 4, pygame.K_6: 6, pygame.K_8: 8}


def _render_button_format_options(screen, font, line_gap, options, selected, prompt):
	screen.fill((0, 0, 0))
	title_y = max(28, line_gap)
	start_y = title_y + line_gap
	draw_centered_text(screen, font, prompt, y=title_y)
	for index, value in enumerate(options):
		prefix = ">" if index == selected else " "
		draw_centered_text(screen, font, f"{prefix} {value} botones", y=start_y + index * line_gap)
	draw_centered_text(screen, font, "Esc para volver", y=screen.get_height() - max(20, line_gap))


def choose_button_format(screen, initial_value=6):
	options = [4, 6, 8]
	prompt = "Selecciona el formato (flechas + Enter):"
	selected = options.index(initial_value) if initial_value in options else 1
	clock = pygame.time.Clock()

	while True:
		lines = [prompt] + [f"{v} botones" for v in options]
		font, line_gap = build_responsive_font(screen, lines, base_size=28, min_size=14, max_size=34, base_resolution=(500, 280))
		_render_button_format_options(screen, font, line_gap, options, selected, prompt)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return None
			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_UP, pygame.K_LEFT):
					selected = (selected - 1) % len(options)
				elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
					selected = (selected + 1) % len(options)
				elif event.key == pygame.K_RETURN:
					return options[selected]
				elif event.key in KEY_TO_VALUE:
					return KEY_TO_VALUE[event.key]
				elif event.key == pygame.K_ESCAPE:
					return None
		clock.tick(60)

