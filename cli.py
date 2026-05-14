import sys

import engine_sys_path  # noqa: F401, E402

from config import RESET_LOG_PATH, get_runtime_version


def print_help():
	print(
		"""Joystick Overlay

Uso:
	joystick-overlay [comando]

Comandos:
	(sin comando)  Ejecuta HUD principal
	run            Ejecuta HUD principal
	config         Abre configuración
	tournament     Abre modo torneo
	doctor         Ejecuta diagnóstico de entorno
	--version      Muestra versión runtime
	--show-reset-log  Muestra reset log
	-h, --help     Muestra esta ayuda
"""
	)


def run():
	from main import main as run_main
	from configure import main as run_config
	from tournament import main as run_tournament
	from doctor import main as run_doctor

	args = sys.argv[1:]
	if not args or args[0] in ("-h", "--help", "help"):
		print_help()
		return
	if args[0] == "--version":
		print(get_runtime_version() or "desconocida")
		return
	if args[0] == "--show-reset-log":
		try:
			with open(RESET_LOG_PATH, "r", encoding="utf-8") as file:
				print(file.read().strip() or "(reset log vacío)")
		except Exception:
			print(f"No existe reset log en {RESET_LOG_PATH}")
		return
	cmd = args[0].strip().lower()
	if cmd == "run":
		run_main()
		return
	if cmd == "config":
		run_config()
		return
	if cmd == "tournament":
		run_tournament()
		return
	if cmd == "doctor":
		run_doctor()
		return
	print(f"Comando desconocido: {cmd}")
	print("Uso: joystick-overlay [run|config|tournament|doctor|--version|--show-reset-log]")


if __name__ == "__main__":
	run()
