# input_reader.py

# --- Lee el Json que creo el *mapper.py para pasarselo al renderizador ---

import pygame
import json
import time
import evdev
from evdev import InputDevice, categorize, ecodes

from config import (
	BINDINGS_PATH, JOYSTICK_BINDINGS_PATH, DEVICE_NAME_FILTER,
	get_button_labels, get_bindings_format_key
)
from utils import (
	get_first_joystick_device,
	list_gamepad_devices_by_capabilities,
	list_keyboard_devices_by_capabilities,
)

bindings = {}

def start_input_listener(mode, button_count, input_state, preferred_device_path=None, preferred_keyboard_path=None):
	global bindings

	if mode in ["teclado", "hitbox"]:
		with open(BINDINGS_PATH, "r") as f:
			bindings_all = json.load(f)
			formato = get_bindings_format_key(button_count)
			bindings = bindings_all[formato]
		listen_keyboard(input_state, button_count, preferred_keyboard_path)
	elif mode == "joystick":
		with open(JOYSTICK_BINDINGS_PATH, "r") as f:
			all_bindings = json.load(f)
			formato = get_bindings_format_key(button_count)
			bindings = all_bindings[formato]
		listen_joystick(input_state, button_count, preferred_device_path)

# ---------------- TECLADO ----------------
def _pygame_key_to_evdev_code(key_value):
	key_name = pygame.key.name(key_value).lower()
	special_map = {
		"up": "KEY_UP",
		"down": "KEY_DOWN",
		"left": "KEY_LEFT",
		"right": "KEY_RIGHT",
		"return": "KEY_ENTER",
		"enter": "KEY_ENTER",
		"space": "KEY_SPACE",
		"escape": "KEY_ESC",
		"left shift": "KEY_LEFTSHIFT",
		"right shift": "KEY_RIGHTSHIFT",
		"left ctrl": "KEY_LEFTCTRL",
		"right ctrl": "KEY_RIGHTCTRL",
		"left alt": "KEY_LEFTALT",
		"right alt": "KEY_RIGHTALT",
		"tab": "KEY_TAB",
		"backspace": "KEY_BACKSPACE",
	}

	evdev_name = special_map.get(key_name)
	if evdev_name is None:
		if len(key_name) == 1 and key_name.isalpha():
			evdev_name = f"KEY_{key_name.upper()}"
		elif len(key_name) == 1 and key_name.isdigit():
			evdev_name = f"KEY_{key_name}"
		elif key_name.startswith("f") and key_name[1:].isdigit():
			evdev_name = f"KEY_{key_name.upper()}"
		else:
			normalized = key_name.replace(" ", "").replace("-", "").upper()
			evdev_name = f"KEY_{normalized}"
	return ecodes.ecodes.get(evdev_name)

def _build_evdev_keyboard_bindings():
	evdev_bindings = {}
	for action, key_value in bindings.items():
		evdev_code = _pygame_key_to_evdev_code(key_value)
		if evdev_code is None:
			return None
		evdev_bindings[action] = evdev_code
	return evdev_bindings

def _listen_keyboard_with_focus(input_state, button_count):
	while True:
		keys = pygame.key.get_pressed()

		dx = dy = 0
		if keys[bindings["Izquierda"]]:
			dx -= 1
		if keys[bindings["Derecha"]]:
			dx += 1
		if keys[bindings["Arriba"]]:
			dy -= 1
		if keys[bindings["Abajo"]]:
			dy += 1

		if dx != 0 and dy != 0:
			dx *= 0.7
			dy *= 0.7

		input_state["stick"] = [dx, dy]

		for i, name in enumerate(get_button_labels(button_count)):
			input_state["buttons"][i] = keys[bindings[name]]

		time.sleep(0.01)

def _open_selected_keyboard_device(preferred_keyboard_path):
	if preferred_keyboard_path:
		try:
			return InputDevice(preferred_keyboard_path)
		except Exception:
			return None

	candidates = list_keyboard_devices_by_capabilities()
	if len(candidates) == 0:
		return None

	selected = candidates[0]
	for extra in candidates[1:]:
		extra.close()
	return selected

def _listen_keyboard_global_evdev(input_state, button_count, preferred_keyboard_path):
	dev = _open_selected_keyboard_device(preferred_keyboard_path)
	if dev is None:
		print("[WARN] Teclado global no disponible, se usara modo con foco.")
		return False

	evdev_bindings = _build_evdev_keyboard_bindings()
	if evdev_bindings is None:
		print("[WARN] No se pudieron convertir todos los keybindings a evdev, se usara modo con foco.")
		dev.close()
		return False

	bindings_by_code = {}
	for action, code in evdev_bindings.items():
		if code not in bindings_by_code:
			bindings_by_code[code] = []
		bindings_by_code[code].append(action)

	pressed_state = {}
	labels = get_button_labels(button_count)

	try:
		print(f"[INFO] Teclado global activo: {dev.name}")
		for event in dev.read_loop():
			if event.type != ecodes.EV_KEY:
				continue

			for action in bindings_by_code.get(event.code, []):
				pressed_state[action] = event.value != 0

			dx = 0
			dy = 0
			if pressed_state.get("Izquierda", False):
				dx -= 1
			if pressed_state.get("Derecha", False):
				dx += 1
			if pressed_state.get("Arriba", False):
				dy -= 1
			if pressed_state.get("Abajo", False):
				dy += 1
			if dx != 0 and dy != 0:
				dx *= 0.7
				dy *= 0.7

			input_state["stick"] = [dx, dy]
			for index, label in enumerate(labels):
				input_state["buttons"][index] = pressed_state.get(label, False)
	except Exception as error:
		print(f"[WARN] Error leyendo teclado global ({error}), se usara modo con foco.")
		return False
	finally:
		dev.close()
	return True

def listen_keyboard(input_state, button_count, preferred_keyboard_path=None):
	if preferred_keyboard_path:
		try:
			success = _listen_keyboard_global_evdev(input_state, button_count, preferred_keyboard_path)
			if success:
				return
			print("[INFO] Fallback a teclado con foco.")
			_listen_keyboard_with_focus(input_state, button_count)
			return
		except Exception as error:
			print(f"[WARN] Teclado global falló, usando foco de ventana: {error}")
			_listen_keyboard_with_focus(input_state, button_count)
			return

	_listen_keyboard_with_focus(input_state, button_count)

# ---------------- JOYSTICK ----------------
def listen_joystick(input_state, button_count, preferred_device_path=None):
	dev = None
	if preferred_device_path:
		try:
			dev = evdev.InputDevice(preferred_device_path)
		except Exception:
			dev = None

	if dev is None:
		candidates = list_gamepad_devices_by_capabilities()
		if candidates:
			dev = candidates[0]
			for extra in candidates[1:]:
				extra.close()

	if dev is None:
		dev = get_first_joystick_device(DEVICE_NAME_FILTER)

	if dev is None:
		print("[ERROR] No se detectó joystick compatible para escuchar entradas.")
		input_state["stick"] = [0, 0]
		input_state["buttons"] = [False] * len(get_button_labels(button_count))
		return

	print(f"[INFO] Leyendo entradas desde: {dev.name}")
	for event in dev.read_loop():
		if event.type == ecodes.EV_ABS:
			absevent = categorize(event)
			if event.code == ecodes.ABS_X:
				input_state["stick"][0] = absevent.event.value / 128.0 - 1
			elif event.code == ecodes.ABS_Y:
				input_state["stick"][1] = absevent.event.value / 128.0 - 1
		elif event.type == ecodes.EV_KEY:
			for i, label in enumerate(get_button_labels(button_count)):
				if event.code == bindings.get(label):
					input_state["buttons"][i] = event.value == 1

