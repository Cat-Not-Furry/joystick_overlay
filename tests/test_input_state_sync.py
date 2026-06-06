"""SEC-002: snapshot thread-safe de input_state."""

import os
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

from core.input_state_sync import (
	bind_input_state_lock,
	create_input_state,
	locked_input_state,
	snapshot_input_state,
)


def test_snapshot_is_copy_not_alias():
	st = create_input_state(4)
	bind_input_state_lock(st)
	with locked_input_state(st) as live:
		live["stick"][0] = 0.5
		live["buttons"][0] = True
	snap = snapshot_input_state(st)
	snap["stick"][0] = -1.0
	snap["buttons"][0] = False
	assert st["stick"][0] == 0.5
	assert st["buttons"][0] is True


def test_concurrent_snapshot_and_write():
	st = create_input_state(2)
	bind_input_state_lock(st)
	errors = []

	def writer():
		try:
			for i in range(50):
				with locked_input_state(st) as live:
					live["stick"][0] = float(i)
		except Exception as exc:
			errors.append(exc)

	def reader():
		try:
			for _ in range(50):
				snap = snapshot_input_state(st)
				assert len(snap["buttons"]) == 2
		except Exception as exc:
			errors.append(exc)

	threads = [threading.Thread(target=writer), threading.Thread(target=reader)]
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	assert not errors
