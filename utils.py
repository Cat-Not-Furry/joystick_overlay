# utils.py

# --- Configuraciones que se repiten ---

import pygame
import evdev
from evdev import InputDevice, ecodes
from config import COLOR_TEXT, SCREEN_WIDTH, SCREEN_HEIGHT

def draw_centered_text(screen, font, text, y, color=COLOR_TEXT, center_x=None):
	if center_x is None:
		center_x = screen.get_width() // 2
	surface = font.render(text, True, color)
	rect = surface.get_rect(center=(center_x, y))
	screen.blit(surface, rect)

def fit_text_to_width(font, text, max_width):
	render_text = str(text)
	if max_width <= 0:
		return render_text
	if font.size(render_text)[0] <= max_width:
		return render_text

	ellipsis = "..."
	allowed = render_text
	while len(allowed) > 0:
		allowed = allowed[:-1]
		candidate = allowed + ellipsis
		if font.size(candidate)[0] <= max_width:
			return candidate
	return ellipsis

def clamp(value, min_value, max_value):
	return max(min_value, min(max_value, value))

def build_responsive_font(
	screen,
	lines,
	base_size=28,
	min_size=14,
	max_size=36,
	base_resolution=(460, 320),
	max_width_ratio=0.92,
	max_height_ratio=0.80,
	line_spacing=1.35,
):
	screen_width = max(1, screen.get_width())
	screen_height = max(1, screen.get_height())
	base_width = max(1, base_resolution[0])
	base_height = max(1, base_resolution[1])

	scale = min(screen_width / base_width, screen_height / base_height)
	current_size = clamp(int(round(base_size * scale)), min_size, max_size)
	render_lines = [str(line) for line in lines] if lines else [""]

	while current_size >= min_size:
		font = pygame.font.SysFont(None, current_size)
		line_gap = max(font.get_height() + 6, int(font.get_height() * line_spacing))

		max_width = 0
		for line in render_lines:
			line_width, _ = font.size(line)
			max_width = max(max_width, line_width)

		total_height = len(render_lines) * line_gap
		fits_width = max_width <= int(screen_width * max_width_ratio)
		fits_height = total_height <= int(screen_height * max_height_ratio)
		if fits_width and fits_height:
			return font, line_gap

		current_size -= 1

	font = pygame.font.SysFont(None, min_size)
	line_gap = max(font.get_height() + 6, int(font.get_height() * line_spacing))
	return font, line_gap

def open_secondary_window(title, size=(460, 260), window_mode="floating_hint"):
	previous_surface = pygame.display.get_surface()
	previous_size = previous_surface.get_size() if previous_surface else (SCREEN_WIDTH, SCREEN_HEIGHT)
	window = pygame.display.set_mode(size, pygame.RESIZABLE)
	if window_mode == "floating_hint" and hasattr(pygame.display, "set_window_size"):
		pygame.display.set_window_size(size[0], size[1])
	pygame.display.set_caption(title)
	return window, previous_size

def restore_primary_window(size, window_mode="floating_hint", title="Arcade HUD Overlay"):
	window = pygame.display.set_mode(size, pygame.RESIZABLE)
	if window_mode == "floating_hint" and hasattr(pygame.display, "set_window_size"):
		pygame.display.set_window_size(size[0], size[1])
	pygame.display.set_caption(title)
	return window

def get_first_joystick_device(name_filters):
	normalized_filters = [name.lower() for name in name_filters]

	for path in evdev.list_devices():
		device = InputDevice(path)
		device_name = device.name.lower()
		if any(name in device_name for name in normalized_filters):
			return device
		device.close()

	return None

def _supports_gamepad_capabilities(device):
	try:
		capabilities = device.capabilities(verbose=False)
		if ecodes.EV_KEY not in capabilities:
			return False
		if ecodes.EV_ABS not in capabilities:
			return False

		abs_entries = capabilities.get(ecodes.EV_ABS, [])
		abs_codes = {entry[0] if isinstance(entry, tuple) else entry for entry in abs_entries}
		has_stick_axes = ecodes.ABS_X in abs_codes and ecodes.ABS_Y in abs_codes
		return has_stick_axes
	except Exception:
		return False

def list_gamepad_devices_by_capabilities():
	results = []
	for path in evdev.list_devices():
		try:
			device = InputDevice(path)
			if _supports_gamepad_capabilities(device):
				results.append(device)
			else:
				device.close()
		except Exception:
			continue
	return results

def find_gamepad_by_name(name_query):
	query = name_query.strip().lower()
	if query == "":
		return None

	for device in list_gamepad_devices_by_capabilities():
		if query in device.name.lower():
			return device
		device.close()
	return None

def _supports_keyboard_capabilities(device):
	try:
		capabilities = device.capabilities(verbose=False)
		if ecodes.EV_KEY not in capabilities:
			return False
		# Evita gamepads/joysticks: normalmente exponen ejes absolutos.
		if ecodes.EV_ABS in capabilities:
			return False

		key_entries = capabilities.get(ecodes.EV_KEY, [])
		key_codes = {entry[0] if isinstance(entry, tuple) else entry for entry in key_entries}
		required_keys = {ecodes.KEY_ENTER, ecodes.KEY_SPACE, ecodes.KEY_ESC}
		has_required = required_keys.issubset(key_codes)
		# Umbral minimo para evitar detectar dispositivos con pocas teclas.
		keyboard_like_size = len(key_codes) >= 20
		return has_required and keyboard_like_size
	except Exception:
		return False

def list_keyboard_devices_by_capabilities():
	results = []
	for path in evdev.list_devices():
		try:
			device = InputDevice(path)
			if _supports_keyboard_capabilities(device):
				results.append(device)
			else:
				device.close()
		except Exception:
			continue
	return results

def show_error_and_exit(screen, message):
	error_lines = message.split('\n')
	running = True
	while running:
		lines = error_lines + ["Presiona cualquier tecla para salir"]
		font, line_gap = build_responsive_font(
			screen,
			lines,
			base_size=28,
			min_size=14,
			max_size=34,
			base_resolution=(460, 260),
		)
		start_y = max(35, (screen.get_height() - line_gap * len(lines)) // 2)

		screen.fill((20, 0, 0))
		for i, line in enumerate(error_lines):
			draw_centered_text(screen, font, line, y=start_y + i * line_gap)
		draw_centered_text(screen, font, "Presiona cualquier tecla para salir", y=start_y + (len(lines) - 1) * line_gap)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				running = False
	pygame.quit()
	exit()
