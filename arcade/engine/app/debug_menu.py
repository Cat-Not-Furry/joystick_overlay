# debug_menu.py — diagnóstico menú / VIDEORESIZE (JOYSTICK_DEBUG_MENU=1)

import os
import time

_debug_videoresize_count = 0
_debug_set_mode_count = 0
_debug_stats_last_sec = 0.0


def debug_menu(msg):
	if os.environ.get("JOYSTICK_DEBUG_MENU") == "1":
		ts = (
			time.strftime("%H:%M:%S", time.localtime())
			+ f".{int((time.time() % 1) * 1000):03d}"
		)
		print(f"[JOYSTICK_DEBUG] {ts} | {msg}")


def debug_count_videoresize():
	global _debug_videoresize_count
	_debug_videoresize_count += 1


def debug_count_set_mode():
	global _debug_set_mode_count
	_debug_set_mode_count += 1


def debug_report_videoresize_stats():
	if os.environ.get("JOYSTICK_DEBUG_MENU") != "1":
		return
	global _debug_videoresize_count, _debug_set_mode_count, _debug_stats_last_sec
	now = time.time()
	if now - _debug_stats_last_sec >= 1.0 and (
		_debug_videoresize_count > 0 or _debug_set_mode_count > 0
	):
		elapsed = now - _debug_stats_last_sec
		vr_per_sec = _debug_videoresize_count / elapsed
		sm_per_sec = _debug_set_mode_count / elapsed
		print(
			f"[JOYSTICK_DEBUG] stats | VIDEORESIZE/s: {vr_per_sec:.1f} | set_mode/s: {sm_per_sec:.1f}"
		)
		_debug_videoresize_count = 0
		_debug_set_mode_count = 0
		_debug_stats_last_sec = now
	elif _debug_stats_last_sec == 0.0:
		_debug_stats_last_sec = now
