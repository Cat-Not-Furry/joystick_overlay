# core/input_state_sync.py — lectura/escritura thread-safe de input_state (SEC-002)

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Callable


def create_input_state(button_count: int) -> dict:
	return {
		"stick": [0.0, 0.0],
		"buttons": [False] * button_count,
		"select": False,
		"start": False,
	}


def bind_input_state_lock(input_state: dict, lock: threading.Lock | None = None) -> threading.Lock:
	lock = lock or threading.Lock()
	input_state["_sync_lock"] = lock
	return lock


def snapshot_input_state(input_state: dict) -> dict:
	lock = input_state.get("_sync_lock")

	def _copy() -> dict:
		return {
			"stick": list(input_state["stick"]),
			"buttons": list(input_state["buttons"]),
			"select": bool(input_state.get("select", False)),
			"start": bool(input_state.get("start", False)),
		}

	if lock is not None:
		with lock:
			return _copy()
	return _copy()


@contextmanager
def locked_input_state(input_state: dict):
	lock = input_state.get("_sync_lock")
	if lock is not None:
		lock.acquire()
	try:
		yield input_state
	finally:
		if lock is not None:
			lock.release()


def mutate_input_state(input_state: dict, mutator: Callable[[dict], None]) -> None:
	with locked_input_state(input_state):
		mutator(input_state)
