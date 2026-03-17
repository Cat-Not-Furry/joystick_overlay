#!/usr/bin/env python3
"""
Ejecuta análisis de complejidad ciclomática con radon.
Falla si alguna función supera el umbral (por defecto 10).
Uso: python test/run_cyclomatic.py [--threshold N] [ruta]
"""

import sys
import os

# Añadir raíz del proyecto al path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

THRESHOLD = 10


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

	try:
		from radon.complexity import cc_visit
	except ImportError:
		print("Instala radon: pip install radon==6.0.1")
		sys.exit(2)

	violations = []
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
			if not name.endswith(".py"):
				continue
			filepath = os.path.join(dirpath, name)
			relpath = os.path.relpath(filepath, ROOT)
			if relpath.startswith("test"):
				continue
			try:
				with open(filepath, "r", encoding="utf-8", errors="replace") as f:
					code = f.read()
			except Exception as e:
				print(f"[WARN] No se pudo leer {relpath}: {e}")
				continue
			try:
				blocks = cc_visit(code)
			except Exception as e:
				print(f"[WARN] Error analizando {relpath}: {e}")
				continue
			for block in blocks:
				if block.complexity > threshold:
					violations.append((relpath, block.name, block.complexity, block.lineno))

	if violations:
		print("Complejidad ciclomática excede umbral {}:".format(threshold))
		for path, name, cc, line in sorted(violations, key=lambda x: (-x[2], x[0])):
			print("  {}:{} {} -> CC={}".format(path, line, name, cc))
		sys.exit(1)
	print("OK: ninguna función supera CC={}".format(threshold))
	sys.exit(0)


if __name__ == "__main__":
	main()
