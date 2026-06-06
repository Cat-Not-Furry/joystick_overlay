# input_reader.py

# --- Lee el Json que creo el *mapper.py para pasarselo al renderizador ---

import pygame
import json
import time
import select
import evdev
from evdev import InputDevice, categorize, ecodes

from config import (
	BINDINGS_PATH,
	JOYSTICK_BINDINGS_PATH,
	DEVICE_NAME_FILTER,
	get_button_labels,
	get_active_bindings_format_key,
)
from utils import (
	get_first_joystick_device,
	list_gamepad_devices_by_capabilities,
	list_keyboard_devices_by_capabilities,
)
from core.input_state_sync import locked_input_state, snapshot_input_state

def _notify_state_update(state_update_callback, source, input_state):
	if callable(state_update_callback):
		try:
			state_update_callback(source, snapshot_input_state(input_state))
		except Exception as error:
			print(f"[WARN] state_update_callback fallo: {error}")


def start_input_listener(
	mode,
	button_count,
	input_state,
	preferred_device_path=None,
	preferred_keyboard_path=None,
	state_update_callback=None,
	layout_four_variant_4a=False,
):
	fmt = get_active_bindings_format_key(
		button_count=button_count, layout_four_variant_4a=layout_four_variant_4a
	)
	if mode in ["teclado", "hitbox", "mixbox"]:
		try:
			with open(BINDINGS_PATH, "r", encoding="utf-8") as f:
				bindings_all = json.load(f)
		except Exception:
			bindings_all = {}
		if not isinstance(bindings_all, dict):
			bindings_all = {}
		local_bindings = bindings_all.get(fmt, {})
		if not isinstance(local_bindings, dict):
			local_bindings = {}
		listen_keyboard(
			input_state,
			button_count,
			local_bindings,
			preferred_keyboard_path,
			state_update_callback=state_update_callback,
		)
	elif mode == "joystick":
		try:
			with open(JOYSTICK_BINDINGS_PATH, "r", encoding="utf-8") as f:
				all_bindings = json.load(f)
		except Exception:
			all_bindings = {}
		if not isinstance(all_bindings, dict):
			all_bindings = {}
		local_bindings = all_bindings.get(fmt, {})
		if not isinstance(local_bindings, dict):
			local_bindings = {}
		listen_joystick(
			input_state,
			button_count,
			local_bindings,
			preferred_device_path,
			state_update_callback=state_update_callback,
		)

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
		if key_value is None:
			continue
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

def _listen_keyboard_with_focus(input_state, button_count, bindings_map, state_update_callback=None):
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

		with locked_input_state(input_state) as st:
			st["stick"] = [dx, dy]
			for index, label in enumerate(labels):
				st["buttons"][index] = _get_pressed_key(keys, bindings_map, label)
			st["select"] = _get_pressed_key(keys, bindings_map, "SELECT")
			st["start"] = _get_pressed_key(keys, bindings_map, "START")
		_notify_state_update(state_update_callback, "keyboard_focus", input_state)

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

def _compute_stick_from_pressed(pressed_state):
	"""Calcula [dx, dy] del stick a partir del estado de teclas direccionales."""
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
	return [dx, dy]


def _update_input_state_from_pressed(input_state, pressed_state, labels):
	"""Actualiza input_state con stick y botones derivados de pressed_state."""
	with locked_input_state(input_state) as st:
		st["stick"] = _compute_stick_from_pressed(pressed_state)
		for index, label in enumerate(labels):
			st["buttons"][index] = bool(pressed_state.get(label, False))
		st["select"] = bool(pressed_state.get("SELECT", False))
		st["start"] = bool(pressed_state.get("START", False))


def _build_bindings_by_code(evdev_bindings):
	"""Construye mapeo code -> [actions] desde evdev_bindings."""
	bindings_by_code = {}
	for action, code in evdev_bindings.items():
		if code not in bindings_by_code:
			bindings_by_code[code] = []
		bindings_by_code[code].append(action)
	return bindings_by_code


def _apply_evdev_key_to_pressed(event, bindings_by_code, pressed_state):
	"""Actualiza pressed_state con un evento EV_KEY."""
	if event.type != ecodes.EV_KEY:
		return
	for action in bindings_by_code.get(event.code, []):
		pressed_state[action] = event.value != 0


def _prepare_global_keyboard(preferred_keyboard_path, bindings_map, button_count):
	"""Prepara dispositivos y bindings para teclado global. Retorna (devices, bindings_by_code, labels) o None."""
	devices = _open_selected_keyboard_devices(preferred_keyboard_path)
	if len(devices) == 0:
		print("[WARN] Teclado global no disponible, se usara modo con foco.")
		return None
	evdev_bindings = _build_evdev_keyboard_bindings(bindings_map)
	if len(evdev_bindings) == 0:
		print("[WARN] No se encontraron keybindings validos para teclado global, se usara modo con foco.")
		for device in devices:
			device.close()
		return None
	labels = get_button_labels(button_count)
	return devices, _build_bindings_by_code(evdev_bindings), labels


def _run_global_keyboard_loop(input_state, devices, bindings_by_code, labels, state_update_callback=None):
	"""Bucle principal de lectura evdev. No retorna (loop infinito)."""
	device_names = ", ".join([device.name for device in devices])
	print(f"[INFO] Teclado global activo: {device_names}")
	pressed_state = {}
	while True:
		ready, _, _ = select.select(devices, [], [], 0.01)
		for device in ready:
			for event in device.read():
				_apply_evdev_key_to_pressed(event, bindings_by_code, pressed_state)
		_update_input_state_from_pressed(input_state, pressed_state, labels)
		_notify_state_update(state_update_callback, "keyboard_global", input_state)


def _listen_keyboard_global_evdev(input_state, button_count, bindings_map, preferred_keyboard_path, state_update_callback=None):
	prepared = _prepare_global_keyboard(preferred_keyboard_path, bindings_map, button_count)
	if prepared is None:
		return False
	devices, bindings_by_code, labels = prepared
	try:
		_run_global_keyboard_loop(
			input_state,
			devices,
			bindings_by_code,
			labels,
			state_update_callback=state_update_callback,
		)
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

def listen_keyboard(input_state, button_count, bindings_map, preferred_keyboard_path=None, state_update_callback=None):
	if preferred_keyboard_path:
		try:
			success = _listen_keyboard_global_evdev(
				input_state,
				button_count,
				bindings_map,
				preferred_keyboard_path,
				state_update_callback=state_update_callback,
			)
			if success:
				return
			print("[INFO] Fallback a teclado con foco.")
			_listen_keyboard_with_focus(
				input_state,
				button_count,
				bindings_map,
				state_update_callback=state_update_callback,
			)
			return
		except Exception as error:
			print(f"[WARN] Teclado global falló, usando foco de ventana: {error}")
			_listen_keyboard_with_focus(
				input_state,
				button_count,
				bindings_map,
				state_update_callback=state_update_callback,
			)
			return

	_listen_keyboard_with_focus(
		input_state,
		button_count,
		bindings_map,
		state_update_callback=state_update_callback,
	)

# ---------------- JOYSTICK ----------------
def _open_joystick_device(preferred_device_path):
	"""Abre dispositivo joystick. Retorna InputDevice o None."""
	if preferred_device_path:
		try:
			return evdev.InputDevice(preferred_device_path)
		except Exception:
			pass
	candidates = list_gamepad_devices_by_capabilities()
	if candidates:
		dev = candidates[0]
		for extra in candidates[1:]:
			extra.close()
		return dev
	return get_first_joystick_device(DEVICE_NAME_FILTER)


def _process_joystick_event(event, input_state, labels, bindings_map):
	"""Procesa un evento del joystick y actualiza input_state."""
	with locked_input_state(input_state) as st:
		if event.type == ecodes.EV_ABS:
			absevent = categorize(event)
			if event.code == ecodes.ABS_X:
				st["stick"][0] = absevent.event.value / 128.0 - 1
			elif event.code == ecodes.ABS_Y:
				st["stick"][1] = absevent.event.value / 128.0 - 1
		elif event.type == ecodes.EV_KEY:
			for i, label in enumerate(labels):
				code = bindings_map.get(label)
				if code is not None and event.code == code:
					st["buttons"][i] = event.value == 1
			sc = bindings_map.get("SELECT")
			if sc is not None and event.code == sc:
				st["select"] = event.value == 1
			stc = bindings_map.get("START")
			if stc is not None and event.code == stc:
				st["start"] = event.value == 1


def listen_joystick(input_state, button_count, bindings_map, preferred_device_path=None, state_update_callback=None):
	dev = _open_joystick_device(preferred_device_path)
	if dev is None:
		print("[ERROR] No se detectó joystick compatible para escuchar entradas.")
		labels = get_button_labels(button_count)
		with locked_input_state(input_state) as st:
			st["stick"] = [0, 0]
			st["buttons"] = [False] * len(labels)
			st["select"] = False
			st["start"] = False
		_notify_state_update(state_update_callback, "joystick", input_state)
		return

	labels = get_button_labels(button_count)
	with locked_input_state(input_state) as st:
		st["select"] = False
		st["start"] = False
	print(f"[INFO] Leyendo entradas desde: {dev.name}")
	for event in dev.read_loop():
		_process_joystick_event(event, input_state, labels, bindings_map)
		_notify_state_update(state_update_callback, "joystick", input_state)

