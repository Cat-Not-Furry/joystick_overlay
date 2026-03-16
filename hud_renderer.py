# hud_renderer.py

# --- Encargado de dibujar todo en la ventana ---

import os
import pygame
from utils import get_ui_font

from config import (
	JOYSTICK_CENTER,
	JOYSTICK_RADIUS,
	JOYSTICK_STICK_LENGTH,
	BUTTON_RADIUS,
	get_icon_paths,
	get_button_positions,
	COLOR_STICK,
	COLOR_STICK_KNOB,
	COLOR_BUTTON_ACTIVE,
	COLOR_BUTTON_INACTIVE,
	COLOR_TEXT,
	get_button_labels,
	get_hud_fallback_text,
)

icons = []
current_controller_style = "default"
current_render_mode = "normal"
current_input_layout = "stick"
current_stick_knob_color = COLOR_STICK_KNOB
current_stick_bar_color = (0, 0, 0)
current_stick_ring_color = (255, 255, 255)

def _normalize_color(color_value, fallback):
	if isinstance(color_value, list) and len(color_value) == 3:
		return tuple(color_value)
	if isinstance(color_value, tuple) and len(color_value) == 3:
		return color_value
	return fallback

def load_icons(button_count, custom_icon_paths=None, enable_icons=True):
	global icons
	icons = []
	labels = get_button_labels(button_count)
	if not enable_icons:
		icons = [None for _ in labels]
		return

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
	global current_stick_knob_color
	current_stick_knob_color = _normalize_color(color, COLOR_STICK_KNOB)

def set_stick_colors(knob_color, bar_color, ring_color):
	global current_stick_knob_color, current_stick_bar_color, current_stick_ring_color
	current_stick_knob_color = _normalize_color(knob_color, COLOR_STICK_KNOB)
	current_stick_bar_color = _normalize_color(bar_color, (0, 0, 0))
	current_stick_ring_color = _normalize_color(ring_color, (255, 255, 255))

def set_controller_style(style):
	global current_controller_style
	current_controller_style = style or "default"

def set_render_mode(render_mode):
	global current_render_mode
	current_render_mode = render_mode if render_mode in ["normal", "tournament"] else "normal"

def set_input_layout(layout_mode):
	global current_input_layout
	current_input_layout = layout_mode if layout_mode in ["stick", "hitbox"] else "stick"

def draw_hud(screen, state, button_count):
	if current_render_mode == "tournament":
		draw_tournament_mode(screen, state, button_count)
		return

	if current_input_layout == "hitbox":
		draw_hitbox_direction_pad(screen, state["stick"])
	else:
		draw_stick(screen, state["stick"])
	draw_buttons(screen, state["buttons"], button_count, text_only=False)

def draw_stick(screen, vec):
	center_x, center_y = JOYSTICK_CENTER
	end_x = int(center_x + vec[0] * JOYSTICK_STICK_LENGTH)
	end_y = int(center_y + vec[1] * JOYSTICK_STICK_LENGTH)

	pygame.draw.circle(screen, COLOR_STICK, (center_x, center_y), JOYSTICK_RADIUS)
	pygame.draw.line(screen, current_stick_bar_color, (center_x, center_y), (end_x, end_y), 6)
	pygame.draw.circle(screen, current_stick_knob_color, (end_x, end_y), 12)

	if abs(vec[0]) > 0.2 or abs(vec[1]) > 0.2:
		pygame.draw.circle(screen, current_stick_ring_color, (end_x, end_y), 16, 2)

def draw_hitbox_direction_pad(screen, vec):
	base_x = 70
	base_y = 80
	size = 24
	gap = 10
	up = vec[1] < -0.3
	down = vec[1] > 0.3
	left = vec[0] < -0.3
	right = vec[0] > 0.3

	def _draw_cell(x, y, label, pressed):
		color = COLOR_BUTTON_ACTIVE if pressed else COLOR_BUTTON_INACTIVE
		rect = pygame.Rect(x, y, size, size)
		pygame.draw.rect(screen, color, rect, border_radius=4)
		font = get_ui_font(16, variant="bold")
		text = font.render(label, True, COLOR_TEXT)
		screen.blit(text, text.get_rect(center=rect.center))

	_draw_cell(base_x + size + gap, base_y - (size + gap), "U", up)
	_draw_cell(base_x, base_y, "L", left)
	_draw_cell(base_x + size + gap, base_y, "D", down)
	_draw_cell(base_x + (size + gap) * 2, base_y, "R", right)

def draw_buttons(screen, button_states, button_count, text_only=False):
	positions = get_button_positions(button_count)
	labels = get_button_labels(button_count)
	label_font = get_ui_font(18, variant="bold")

	for index, pos in enumerate(positions):
		icon = icons[index] if index < len(icons) else None
		pressed = button_states[index]

		if icon and not text_only:
			rect = icon.get_rect(center=pos)
			screen.blit(icon, rect)
			if pressed:
				pygame.draw.circle(screen, COLOR_BUTTON_ACTIVE, pos, BUTTON_RADIUS, 3)
			continue

		color = COLOR_BUTTON_ACTIVE if pressed else COLOR_BUTTON_INACTIVE
		pygame.draw.circle(screen, color, pos, BUTTON_RADIUS)
		label = get_hud_fallback_text(labels[index], current_controller_style)
		label_surface = label_font.render(label, True, COLOR_TEXT)
		label_rect = label_surface.get_rect(center=pos)
		screen.blit(label_surface, label_rect)

def draw_tournament_mode(screen, state, button_count):
	# Render minimalista para reducir costo de CPU y mantener legibilidad.
	if current_input_layout == "hitbox":
		draw_hitbox_direction_pad(screen, state["stick"])
	else:
		draw_stick(screen, state["stick"])
	draw_buttons(screen, state["buttons"], button_count, text_only=True)

