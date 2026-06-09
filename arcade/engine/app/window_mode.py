# window_mode.py — modo ventana flotante/normal (sincronizado desde main)

_current_window_mode = "floating_hint"


def get_window_mode():
	return _current_window_mode


def set_window_mode(value):
	global _current_window_mode
	_current_window_mode = value
