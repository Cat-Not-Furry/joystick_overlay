#!/usr/bin/env python3
"""Pruebas de extracción ZIP segura e import de perfil (stdlib + engine path)."""

import json
import os
import stat
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

from utils.safe_zip_extract import SafeZipExtractError, extract_zip_safely


def test_extract_rejects_dotdot_member():
	with tempfile.TemporaryDirectory() as tmp:
		zpath = os.path.join(tmp, "bad.zip")
		dst = os.path.join(tmp, "out")
		with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
			zf.writestr("../evil.txt", b"x")
		try:
			extract_zip_safely(zpath, dst)
			assert False, "expected SafeZipExtractError"
		except SafeZipExtractError:
			pass


def test_extract_rejects_too_many_members():
	with tempfile.TemporaryDirectory() as tmp:
		zpath = os.path.join(tmp, "many.zip")
		dst = os.path.join(tmp, "out")
		with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
			for i in range(10):
				zf.writestr(f"f{i}.txt", b"a")
		try:
			extract_zip_safely(zpath, dst, max_members=5)
			assert False, "expected SafeZipExtractError"
		except SafeZipExtractError as e:
			assert "demasiados" in str(e).lower()


def test_extract_accepts_legit_profile_layout():
	with tempfile.TemporaryDirectory() as tmp:
		zpath = os.path.join(tmp, "ok.zip")
		dst = os.path.join(tmp, "out")
		with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
			zf.writestr(
				"profile.json",
				json.dumps({"name": "Z", "id": "z1", "button_count": 6, "input_mode": "teclado"}),
			)
			zf.writestr("bindings/key_bindings.json", b"{}")
		extract_zip_safely(zpath, dst)
		assert os.path.isfile(os.path.join(dst, "profile.json"))


def test_extract_rejects_symlink_member_if_unix_zip():
	zi = zipfile.ZipInfo("thelink")
	zi.create_system = 3
	zi.external_attr = (stat.S_IFLNK | 0o777) << 16
	with tempfile.TemporaryDirectory() as tmp:
		zpath = os.path.join(tmp, "sym.zip")
		dst = os.path.join(tmp, "out")
		with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
			zf.writestr(zi, b"/tmp/foo")
		try:
			extract_zip_safely(zpath, dst)
		except SafeZipExtractError:
			return
		link_path = os.path.join(dst, "thelink")
		assert not os.path.lexists(link_path), "miembro symlink no debio extraerse sin error"


def test_resolve_under_root_rejects_escape():
	from utils.safe_paths import resolve_under_root

	with tempfile.TemporaryDirectory() as tmp:
		root = os.path.join(tmp, "prof")
		os.makedirs(os.path.join(root, "icons"), exist_ok=True)
		f = os.path.join(root, "icons", "a.png")
		with open(f, "wb") as fh:
			fh.write(b"\x89PNG\r\n\x1a\n")
		assert resolve_under_root(root, "icons/a.png") == f
		assert resolve_under_root(root, "../../../etc/passwd") is None


def main():
	test_extract_rejects_dotdot_member()
	test_extract_rejects_too_many_members()
	test_extract_accepts_legit_profile_layout()
	test_extract_rejects_symlink_member_if_unix_zip()
	test_resolve_under_root_rejects_escape()
	print("OK: test_zip_security")


if __name__ == "__main__":
	main()
