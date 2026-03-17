#!/usr/bin/env python3
"""
Analiza acoplamiento entre módulos (CBO aproximado vía imports).
Lista imports por módulo y falla si algún módulo supera el umbral.
Uso: python test/run_cbo.py [--threshold N] [ruta]
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

THRESHOLD = 15


def get_py_files(path):
	"""Genera rutas de archivos .py del proyecto, excluyendo test/, venv, .venv."""
	skip_dirs = {".venv", "venv", "__pycache__", ".git"}
	for dirpath, dirnames, filenames in os.walk(path):
		dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith(".")]
		rel = os.path.relpath(dirpath, ROOT)
		if rel.startswith("test") and rel != "test":
			continue
		if "test" in rel.split(os.sep) and rel != "test":
			continue
		if ".venv" in rel or "venv" in rel or "__pycache__" in rel:
			continue
		for name in filenames:
			if name.endswith(".py"):
				filepath = os.path.join(dirpath, name)
				relpath = os.path.relpath(filepath, ROOT)
				if relpath.startswith("test"):
					continue
				yield filepath, relpath


def count_imports(filepath):
	"""Cuenta módulos importados (from X import Y e import X) en un archivo."""
	imports = set()
	try:
		with open(filepath, "r", encoding="utf-8", errors="replace") as f:
			tree = ast.parse(f.read())
	except Exception:
		return 0
	for node in ast.walk(tree):
		if isinstance(node, ast.Import):
			for alias in node.names:
				mod = alias.name.split(".")[0]
				if mod:
					imports.add(mod)
		elif isinstance(node, ast.ImportFrom):
			if node.module:
				imports.add(node.module.split(".")[0])
	return len(imports)


def main():
	threshold = THRESHOLD
	args = sys.argv[1:]
	if args and args[0].startswith("--threshold"):
		if args[0] == "--threshold" and len(args) > 1:
			threshold = int(args[1])
			args = args[2:]
		elif "=" in args[0]:
			threshold = int(args[0].split("=")[1])
			args = args[1:]
	path = args[0] if args else ROOT

	results = []
	for filepath, relpath in get_py_files(path):
		count = count_imports(filepath)
		results.append((relpath, count))

	violations = [(r, c) for r, c in results if c > threshold]
	results.sort(key=lambda x: -x[1])

	print("=== Acoplamiento (imports por módulo) ===\n")
	for relpath, count in results:
		mark = " [EXCEDE]" if count > threshold else ""
		print("  {}: {} imports{}".format(relpath, count, mark))

	if violations:
		print("\nMódulos que exceden umbral {}:".format(threshold))
		for r, c in violations:
			print("  {} -> {} imports".format(r, c))
		sys.exit(1)
	print("\nOK: ningún módulo supera {} imports.".format(threshold))
	sys.exit(0)


if __name__ == "__main__":
	main()
