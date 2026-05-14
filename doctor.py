import os
import grp
import pwd
import getpass

import engine_sys_path  # noqa: F401, E402

from config import get_user_dir, BACKUP_PROFILES_ROOT


def _is_user_in_group(group_name):
	user = getpass.getuser()
	try:
		user_info = pwd.getpwnam(user)
	except KeyError:
		return False
	try:
		group_info = grp.getgrnam(group_name)
	except KeyError:
		return False
	if user_info.pw_gid == group_info.gr_gid:
		return True
	return user in group_info.gr_mem


def _check_dev_input():
	return os.path.isdir("/dev/input")


def _check_event_devices():
	if not os.path.isdir("/dev/input"):
		return 0
	count = 0
	for name in os.listdir("/dev/input"):
		if name.startswith("event"):
			count += 1
	return count


def _detect_graphics_session():
	wayland = os.environ.get("WAYLAND_DISPLAY")
	display = os.environ.get("DISPLAY")
	session_type = os.environ.get("XDG_SESSION_TYPE", "")
	desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
	if wayland:
		return "wayland", session_type, desktop
	if display:
		return "x11", session_type, desktop
	return "tty", session_type, desktop


def main():
	print("== Joystick Overlay Doctor ==")
	print(f"INFO Datos (canon): {get_user_dir()}")
	print(f"INFO Ruta espejo opcional (si esta activado en perfil): {BACKUP_PROFILES_ROOT}")
	session, session_type, desktop = _detect_graphics_session()
	if session == "wayland":
		print("WARN Sesion grafica: Wayland detectado")
		print("     En algunos entornos el overlay puede mostrar comportamiento limitado.")
		print("     Sugerencia: si notas fallos, prueba sesión X11.")
	elif session == "x11":
		print("OK  Sesion grafica: X11 detectado")
	else:
		print("ERR Sesion grafica: no detectada (TTY o shell sin entorno grafico)")
		print("     El HUD requiere ejecutar desde X11 o Wayland.")
		print("     Abre una sesión gráfica y vuelve a ejecutar el comando.")
	if session_type:
		print(f"INFO XDG_SESSION_TYPE={session_type}")
	if desktop:
		print(f"INFO XDG_CURRENT_DESKTOP={desktop}")

	if _check_dev_input():
		print("OK  /dev/input encontrado")
	else:
		print("ERR /dev/input no existe en este sistema")

	event_count = _check_event_devices()
	if event_count > 0:
		print(f"OK  Dispositivos event detectados: {event_count}")
	else:
		print("WARN No se detectaron /dev/input/event*")

	if _is_user_in_group("input"):
		print("OK  Usuario dentro del grupo input")
	else:
		print("WARN Usuario fuera del grupo input")
		print("     Sugerido: sudo usermod -aG input $USER")

	try:
		import pygame  # noqa: F401
		print("OK  pygame disponible")
	except Exception as error:
		print(f"ERR pygame no disponible: {error}")

	try:
		import evdev  # noqa: F401
		print("OK  evdev disponible")
	except Exception as error:
		print(f"ERR evdev no disponible: {error}")

	print("Sugerencia: usa 'joystick-overlay config' para revisar modo y perfiles.")


if __name__ == "__main__":
	main()
