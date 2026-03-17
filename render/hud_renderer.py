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
	HITBOX_MIXBOX_DIRECTION_LEFT,
	get_hud_scale,
	get_icon_paths,
	get_button_positions,
	get_button_positions_hitbox_mixbox,
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
current_hitbox_alt_layout = False
current_stick_knob_color = COLOR_STICK_KNOB
current_stick_bar_color = (0, 0, 0)
current_stick_ring_color = (255, 255, 255)
current_button_inactive_color = COLOR_BUTTON_INACTIVE
current_button_active_color = COLOR_BUTTON_ACTIVE

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
	prev = current_input_layout
	current_input_layout = layout_mode if layout_mode in ["stick", "hitbox", "mixbox"] else "stick"
	if current_input_layout != prev:
		print(f"[INFO] Modo overlay: {current_input_layout}.")


def set_hitbox_alt_layout(alt):
	global current_hitbox_alt_layout
	prev = current_hitbox_alt_layout
	current_hitbox_alt_layout = bool(alt)
	if current_hitbox_alt_layout != prev:
		print(f"[INFO] Posicion Hitbox alternativa: {'On' if current_hitbox_alt_layout else 'Off'}.")


def set_button_colors(inactive_color, active_color):
	global current_button_inactive_color, current_button_active_color
	current_button_inactive_color = _normalize_color(inactive_color, COLOR_BUTTON_INACTIVE)
	current_button_active_color = _normalize_color(active_color, COLOR_BUTTON_ACTIVE)

def draw_hud(screen, state, button_count):
	if current_render_mode == "tournament":
		draw_tournament_mode(screen, state, button_count)
		return

	if current_input_layout == "mixbox":
		draw_mixbox_direction_pad(screen, state["stick"])
	elif current_input_layout == "hitbox":
		draw_hitbox_direction_pad(screen, state["stick"])
	else:
		draw_stick(screen, state["stick"])
	draw_buttons(screen, state["buttons"], button_count, text_only=False)

def _get_scale(screen):
	return get_hud_scale(screen.get_width(), screen.get_height())


def draw_stick(screen, vec):
	scale = _get_scale(screen)
	center_x = int(JOYSTICK_CENTER[0] * scale)
	center_y = int(JOYSTICK_CENTER[1] * scale)
	stick_len = int(JOYSTICK_STICK_LENGTH * scale)
	radius = int(JOYSTICK_RADIUS * scale)
	knob_radius = max(4, int(12 * scale))
	ring_radius = max(6, int(16 * scale))
	line_width = max(2, int(6 * scale))

	end_x = int(center_x + vec[0] * stick_len)
	end_y = int(center_y + vec[1] * stick_len)

	pygame.draw.circle(screen, COLOR_STICK, (center_x, center_y), radius)
	pygame.draw.line(screen, current_stick_bar_color, (center_x, center_y), (end_x, end_y), line_width)
	pygame.draw.circle(screen, current_stick_knob_color, (end_x, end_y), knob_radius)

	if abs(vec[0]) > 0.2 or abs(vec[1]) > 0.2:
		pygame.draw.circle(screen, current_stick_ring_color, (end_x, end_y), ring_radius, max(1, int(2 * scale)))

def draw_hitbox_direction_pad(screen, vec):
	"""Hitbox: botones circulares (arcade). Layout L-U-D | R o posición alternativa L-U-D en fila. Mismo radio que botones de impacto."""
	scale = _get_scale(screen)
	base_x = int(HITBOX_MIXBOX_DIRECTION_LEFT * scale)
	base_y = int(85 * scale)
	radius = max(8, int(BUTTON_RADIUS * scale))
	gap = max(4, int(8 * scale))
	screen_h = screen.get_height()
	max_d_vertical = min(base_y - radius, screen_h - base_y - radius)
	d = min(radius * 2 + gap, max(max_d_vertical, radius))
	font_size = max(10, int(18 * scale))

	up = vec[1] < -0.3
	down = vec[1] > 0.3
	left = vec[0] < -0.3
	right = vec[0] > 0.3

	def _draw_circle(x, y, label, pressed):
		color = current_button_active_color if pressed else current_button_inactive_color
		center = (x, y)
		pygame.draw.circle(screen, color, center, radius)
		font = get_ui_font(font_size, variant="bold")
		text = font.render(label, True, COLOR_TEXT)
		screen.blit(text, text.get_rect(center=center))
	if current_hitbox_alt_layout:
		_draw_circle(base_x, base_y, "L", left)
		_draw_circle(base_x + d, base_y, "U", up)
		_draw_circle(base_x + d * 2, base_y, "D", down)
		_draw_circle(base_x + d * 4, base_y, "R", right)
	else:
		_draw_circle(base_x, base_y - d, "L", left)
		_draw_circle(base_x, base_y, "U", up)
		_draw_circle(base_x, base_y + d, "D", down)
		_draw_circle(base_x + d * 3, base_y, "R", right)


def draw_mixbox_direction_pad(screen, vec):
	"""Mixbox: teclas rectangulares (estilo teclado). Layout ↑ arriba; ←↓→ en fila. Direccionales a la izquierda."""
	scale = _get_scale(screen)
	base_x = int(HITBOX_MIXBOX_DIRECTION_LEFT * scale)
	base_y = int(85 * scale)
	w = max(24, int(36 * scale))
	h = max(20, int(28 * scale))
	gap = max(4, int(6 * scale))
	font_size = max(10, int(18 * scale))
	border_radius = max(2, int(6 * scale))

	up = vec[1] < -0.3
	down = vec[1] > 0.3
	left = vec[0] < -0.3
	right = vec[0] > 0.3

	def _draw_rect(x, y, label, pressed):
		color = current_button_active_color if pressed else current_button_inactive_color
		rect = pygame.Rect(x, y, w, h)
		pygame.draw.rect(screen, color, rect, border_radius=border_radius)
		font = get_ui_font(font_size, variant="bold")
		text = font.render(label, True, COLOR_TEXT)
		screen.blit(text, text.get_rect(center=rect.center))

	_draw_rect(base_x + w + gap, base_y - (h + gap), "\u2191", up)
	_draw_rect(base_x, base_y, "\u2190", left)
	_draw_rect(base_x + w + gap, base_y, "\u2193", down)
	_draw_rect(base_x + (w + gap) * 2, base_y, "\u2192", right)

def draw_buttons(screen, button_states, button_count, text_only=False):
	scale = _get_scale(screen)
	if current_input_layout in ("hitbox", "mixbox"):
		positions = get_button_positions_hitbox_mixbox(button_count, screen.get_width(), screen.get_height())
	else:
		positions = get_button_positions(button_count, screen.get_width(), screen.get_height())
	labels = get_button_labels(button_count)
	label_font_size = max(10, int(18 * scale))
	label_font = get_ui_font(label_font_size, variant="bold")
	radius = int(BUTTON_RADIUS * scale)
	icon_size = int(BUTTON_RADIUS * 2 * scale)

	for index, pos in enumerate(positions):
		icon = icons[index] if index < len(icons) else None
		pressed = button_states[index]

		if icon and not text_only:
			scaled_icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
			rect = scaled_icon.get_rect(center=pos)
			screen.blit(scaled_icon, rect)
			if pressed:
				pygame.draw.circle(screen, current_button_active_color, pos, radius, max(1, int(3 * scale)))
			continue

		color = current_button_active_color if pressed else current_button_inactive_color
		pygame.draw.circle(screen, color, pos, radius)
		label = get_hud_fallback_text(labels[index], current_controller_style)
		label_surface = label_font.render(label, True, COLOR_TEXT)
		label_rect = label_surface.get_rect(center=pos)
		screen.blit(label_surface, label_rect)

def draw_tournament_mode(screen, state, button_count):
	# Render minimalista para reducir costo de CPU y mantener legibilidad.
	if current_input_layout == "mixbox":
		draw_mixbox_direction_pad(screen, state["stick"])
	elif current_input_layout == "hitbox":
		draw_hitbox_direction_pad(screen, state["stick"])
	else:
		draw_stick(screen, state["stick"])
	draw_buttons(screen, state["buttons"], button_count, text_only=True)

