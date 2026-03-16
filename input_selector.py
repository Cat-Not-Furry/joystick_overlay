# input_selector.py

# --- Pregunta por el metodo de entrada ---

from utils import draw_centered_text, build_responsive_font
import pygame

# Pregunta que metodo de entrada va a utilizar

def choose_input_mode(screen, initial_mode="teclado"):
	options = ["teclado", "joystick", "hitbox"]
	prompt = "Selecciona entrada (flechas + Enter):"
	selected = options.index(initial_mode) if initial_mode in options else 0
	clock = pygame.time.Clock()

	while True:
		lines = [prompt] + [option.upper() for option in options]
		font, line_gap = build_responsive_font(
			screen,
			lines,
			base_size=28,
			min_size=14,
			max_size=34,
			base_resolution=(500, 280),
		)
		screen.fill((0, 0, 0))
		title_y = max(28, line_gap)
		start_y = title_y + line_gap
		draw_centered_text(screen, font, prompt, y=title_y)
		for index, option in enumerate(options):
			prefix = ">" if index == selected else " "
			draw_centered_text(screen, font, f"{prefix} {option.upper()}", y=start_y + index * line_gap)
		draw_centered_text(screen, font, "Esc para volver", y=screen.get_height() - max(20, line_gap))
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
				elif event.key == pygame.K_t:
					return "teclado"
				elif event.key == pygame.K_j:
					return "joystick"
				elif event.key == pygame.K_h:
					return "hitbox"
				elif event.key == pygame.K_ESCAPE:
					return None
		clock.tick(60)

