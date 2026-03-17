# input_reader.py

# --- Lee el Json que creo el *mapper.py para pasarselo al renderizador ---

import pygame
import json
import time
import select
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

def start_input_listener(mode, button_count, input_state, preferred_device_path=None, preferred_keyboard_path=None):
	if mode in ["teclado", "hitbox", "mixbox"]:
		with open(BINDINGS_PATH, "r") as f:
			bindings_all = json.load(f)
			formato = get_bindings_format_key(button_count)
			local_bindings = bindings_all.get(formato, {})
		listen_keyboard(input_state, button_count, local_bindings, preferred_keyboard_path)
	elif mode == "joystick":
		with open(JOYSTICK_BINDINGS_PATH, "r") as f:
			all_bindings = json.load(f)
			formato = get_bindings_format_key(button_count)
			local_bindings = all_bindings.get(formato, {})
		listen_joystick(input_state, button_count, local_bindings, preferred_device_path)

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

def _build_evdev_keyboard_bindings(bindings_map):
	evdev_bindings = {}
	for action, key_value in bindings_map.items():
		evdev_code = _pygame_key_to_evdev_code(key_value)
		if evdev_code is not None:
			evdev_bindings[action] = evdev_code
	return evdev_bindings

def _get_pressed_key(keys, bindings_map, action):
	key_code = bindings_map.get(action)
	if not isinstance(key_code, int):
		return False
	if key_code < 0 or key_code >= len(keys):
		return False
	return bool(keys[key_code])

def _listen_keyboard_with_focus(input_state, button_count, bindings_map):
	labels = get_button_labels(button_count)
	while True:
		keys = pygame.key.get_pressed()

		dx = dy = 0
		if _get_pressed_key(keys, bindings_map, "Izquierda"):
			dx -= 1
		if _get_pressed_key(keys, bindings_map, "Derecha"):
			dx += 1
		if _get_pressed_key(keys, bindings_map, "Arriba"):
			dy -= 1
		if _get_pressed_key(keys, bindings_map, "Abajo"):
			dy += 1

		if dx != 0 and dy != 0:
			dx *= 0.7
			dy *= 0.7

		input_state["stick"] = [dx, dy]

		for index, label in enumerate(labels):
			input_state["buttons"][index] = _get_pressed_key(keys, bindings_map, label)

		time.sleep(0.01)

def _open_selected_keyboard_devices(preferred_keyboard_path):
	devices = []
	if preferred_keyboard_path:
		try:
			devices.append(InputDevice(preferred_keyboard_path))
			return devices
		except Exception:
			pass

	candidates = list_keyboard_devices_by_capabilities()
	for device in candidates:
		devices.append(device)
	return devices

def _listen_keyboard_global_evdev(input_state, button_count, bindings_map, preferred_keyboard_path):
	devices = _open_selected_keyboard_devices(preferred_keyboard_path)
	if len(devices) == 0:
		print("[WARN] Teclado global no disponible, se usara modo con foco.")
		return False

	evdev_bindings = _build_evdev_keyboard_bindings(bindings_map)
	if len(evdev_bindings) == 0:
		print("[WARN] No se encontraron keybindings validos para teclado global, se usara modo con foco.")
		for device in devices:
			device.close()
		return False

	bindings_by_code = {}
	for action, code in evdev_bindings.items():
		if code not in bindings_by_code:
			bindings_by_code[code] = []
		bindings_by_code[code].append(action)

	pressed_state = {}
	labels = get_button_labels(button_count)

	try:
		device_names = ", ".join([device.name for device in devices])
		print(f"[INFO] Teclado global activo: {device_names}")
		while True:
			ready, _, _ = select.select(devices, [], [], 0.01)
			for device in ready:
				for event in device.read():
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
				input_state["buttons"][index] = bool(pressed_state.get(label, False))
	except Exception as error:
		print(f"[WARN] Error leyendo teclado global ({error}), se usara modo con foco.")
		return False
	finally:
		for device in devices:
			try:
				device.close()
			except Exception:
				pass
	return True

def listen_keyboard(input_state, button_count, bindings_map, preferred_keyboard_path=None):
	if preferred_keyboard_path:
		try:
			success = _listen_keyboard_global_evdev(input_state, button_count, bindings_map, preferred_keyboard_path)
			if success:
				return
			print("[INFO] Fallback a teclado con foco.")
			_listen_keyboard_with_focus(input_state, button_count, bindings_map)
			return
		except Exception as error:
			print(f"[WARN] Teclado global falló, usando foco de ventana: {error}")
			_listen_keyboard_with_focus(input_state, button_count, bindings_map)
			return

	_listen_keyboard_with_focus(input_state, button_count, bindings_map)

# ---------------- JOYSTICK ----------------
def listen_joystick(input_state, button_count, bindings_map, preferred_device_path=None):
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
				if event.code == bindings_map.get(label):
					input_state["buttons"][i] = event.value == 1

