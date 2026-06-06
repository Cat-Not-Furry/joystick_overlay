# main.py

# ---Archivo principal ---

import engine_sys_path  # noqa: F401, E402 — debe ir antes de imports locales arcade/engine

import os
os.environ.setdefault("SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR", "0")

import pygame
import threading
import sys
import subprocess
import tempfile
import json
import time
import shutil


def _debug_menu(msg):
    if os.environ.get("JOYSTICK_DEBUG_MENU") == "1":
        ts = (
            time.strftime("%H:%M:%S", time.localtime())
            + f".{int((time.time() % 1) * 1000):03d}"
        )
        print(f"[JOYSTICK_DEBUG] {ts} | {msg}")


_debug_videoresize_count = 0
_debug_set_mode_count = 0
_debug_stats_last_sec = 0.0


def _debug_count_videoresize():
    global _debug_videoresize_count
    _debug_videoresize_count += 1


def _debug_count_set_mode():
    global _debug_set_mode_count
    _debug_set_mode_count += 1


def _debug_report_videoresize_stats():
    if os.environ.get("JOYSTICK_DEBUG_MENU") != "1":
        return
    global _debug_videoresize_count, _debug_set_mode_count, _debug_stats_last_sec
    now = time.time()
    if now - _debug_stats_last_sec >= 1.0 and (_debug_videoresize_count > 0 or _debug_set_mode_count > 0):
        elapsed = now - _debug_stats_last_sec
        vr_per_sec = _debug_videoresize_count / elapsed
        sm_per_sec = _debug_set_mode_count / elapsed
        print(f"[JOYSTICK_DEBUG] stats | VIDEORESIZE/s: {vr_per_sec:.1f} | set_mode/s: {sm_per_sec:.1f}")
        _debug_videoresize_count = 0
        _debug_set_mode_count = 0
        _debug_stats_last_sec = now
    elif _debug_stats_last_sec == 0.0:
        _debug_stats_last_sec = now


from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    TOURNAMENT_FPS,
    WINDOW_CAPTION_APP,
    get_button_labels,
    get_background_color,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    VIDEORESIZE_COOLDOWN_MS,
    VIDEORESIZE_TOLERANCE_PX,
    EASTEREGG_ENABLE_MULTI_INSTANCE,
    EASTEREGG_MULTI_INSTANCE_KEY,
    EASTEREGG_MAX_INSTANCES,
    DATA_VERSION_PATH,
    ASSETS_VERSION_PATH,
    RUNTIME_VERSION_PATH,
    USER_DIR,
    PROFILES_DIR,
    RESET_LOG_PATH,
    USER_BACKUPS_DIR,
    BACKUP_PROFILES_ROOT,
    ensure_contract_dirs,
    get_active_bindings_format_key,
    get_data_version,
    get_assets_version,
    get_runtime_version,
    write_data_version,
)
from render import choose_button_format, choose_input_mode, open_profile_config_menu
from render.backup_welcome import run_backup_welcome_if_needed
from render.first_run_wizard import run_first_run_wizard_if_needed
from render import (
    draw_hud,
    load_icons,
    load_system_icons,
    set_stick_color,
    set_stick_colors,
    set_button_colors,
)
from render import (
    set_controller_style,
    set_render_mode,
    set_input_layout,
    set_hitbox_alt_layout,
)
from maps import (
    map_keys,
    map_joystick_buttons,
    run_joystick_diagnostic,
    start_input_listener,
)
from profiles import (
    load_profiles_data,
    save_profiles_data,
    get_active_profile,
    sync_active_profile_to_legacy_files,
)
from profiles.hud_layout import resolve_hud_layout_offsets
from core.input_state_sync import (
    bind_input_state_lock,
    create_input_state,
    snapshot_input_state,
)
from utils import (
    draw_centered_text,
    build_responsive_font,
    fit_text_to_width,
    list_keyboard_devices_by_capabilities,
    set_ui_font_family,
    track_set_mode,
    get_last_set_mode_time_ms,
    MenuArrowRepeater,
)
from training import (
    create_training_state,
    start_recording,
    stop_recording,
    clear_sequence,
    start_playback,
    snapshot_if_recording,
    update_playback,
    has_sequence,
    sequence_to_dict,
)
from core.state_manager import BaseState, StateManager
from core.extensions_runtime import emit_hook, set_extensions_enabled
from core.input_history import InputHistory
from core.assets_resolver import resolve_icons_map, clear_cache as clear_assets_cache
from core.data_migrations import CURRENT_DATA_VERSION, migrate_if_needed

# Funcines Principales
MENU_WIDTH = 320
MENU_HEIGHT = 180
SELECTOR_WINDOW_SIZE = (500, 300)
MAPPER_WINDOW_SIZE = (620, 380)
CONFIRM_WINDOW_SIZE = (420, 230)


def _set_window_size(width, height, title):
    _debug_menu(f"_set_window_size({width}x{height})")
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(title)
    track_set_mode()
    return screen


def _count_running_overlay_instances():
    current_pid = os.getpid()
    count = 0
    for pid_text in os.listdir("/proc"):
        if not pid_text.isdigit():
            continue
        pid = int(pid_text)
        if pid == current_pid:
            continue
        cmdline_path = f"/proc/{pid_text}/cmdline"
        try:
            with open(cmdline_path, "rb") as cmdline_file:
                raw = cmdline_file.read().decode("utf-8", errors="ignore")
        except Exception:
            continue
        cmdline = raw.replace("\x00", " ").strip()
        if "python" in cmdline and "main.py" in cmdline:
            count += 1
    return count


def _launch_training_window(sequence_data):
    """Lanza ventana de entrenamiento independiente con la secuencia."""
    fd, path = tempfile.mkstemp(suffix=".json", prefix="joystick_training_")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(sequence_data, f, indent=2)
        standalone_path = os.path.join(
            os.path.dirname(__file__), "training", "standalone.py"
        )
        subprocess.Popen(
            [sys.executable, standalone_path, path],
            cwd=os.path.dirname(__file__),
            start_new_session=True,
        )
    except Exception as err:
        print(f"[WARN] No se pudo abrir ventana de entrenamiento: {err}")
        try:
            os.unlink(path)
        except Exception:
            pass


def _launch_easteregg_instance():
    # Easteregg: permite abrir nuevas instancias para comparar dispositivos.
    if not EASTEREGG_ENABLE_MULTI_INSTANCE:
        return False
    if _count_running_overlay_instances() + 1 >= EASTEREGG_MAX_INSTANCES:
        print(f"[WARN] Limite de instancias alcanzado ({EASTEREGG_MAX_INSTANCES}).")
        return False

    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    try:
        subprocess.Popen(
            [sys.executable, main_path],
            cwd=os.path.dirname(__file__),
            start_new_session=True,
        )
        print("[INFO] Easteregg activado: nueva instancia iniciada.")
        return True
    except Exception as error:
        print(f"[WARN] No se pudo abrir una nueva instancia: {error}")
        return False


def _run_secondary_selector(screen, title, size, runner):
    """Ejecuta selector en la misma superficie (sin cambiar set_mode)."""
    result = runner(screen)
    return result, screen


def select_profile_secondary(profile_data, screen, title="Selecciona perfil"):
    def _runner(screen):
        clock = pygame.time.Clock()
        profiles = profile_data["profiles"]
        selected = 0
        for index, profile in enumerate(profiles):
            if profile["id"] == profile_data.get("active_profile"):
                selected = index
                break

        repeater = MenuArrowRepeater()
        while True:
            profile_names = [profile["name"] for profile in profiles]
            lines = [title] + profile_names[:6] + ["Flechas + Enter | Esc"]
            font, line_gap = build_responsive_font(
                screen,
                lines,
                base_size=28,
                min_size=14,
                max_size=34,
                base_resolution=SELECTOR_WINDOW_SIZE,
                max_height_ratio=0.82,
            )
            screen.fill((0, 0, 0))
            title_y = max(28, line_gap)
            draw_centered_text(screen, font, title, y=title_y)
            start_index = max(0, selected - 2)
            end_index = min(len(profiles), start_index + 5)
            visible = profiles[start_index:end_index]
            start_y = title_y + line_gap
            for visible_index, profile in enumerate(visible):
                option_index = start_index + visible_index
                prefix = ">" if option_index == selected else " "
                draw_centered_text(
                    screen,
                    font,
                    f"{prefix} {profile['name']}",
                    y=start_y + visible_index * line_gap,
                )
            draw_centered_text(
                screen,
                font,
                "Flechas + Enter | Esc",
                y=screen.get_height() - max(20, line_gap),
            )
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key in (
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ):
                        dnav = repeater.consume_keydown(event)
                        if dnav is not None:
                            selected = (selected + dnav) % len(profiles)
                    else:
                        repeater.reset()
                        if event.key == pygame.K_ESCAPE:
                            return None
                        elif event.key == pygame.K_RETURN:
                            return profiles[selected]["id"]
            d2 = repeater.tick_held()
            if d2 is not None:
                selected = (selected + d2) % len(profiles)
            clock.tick(FPS)

    selected_id, screen = _run_secondary_selector(
        screen, title, SELECTOR_WINDOW_SIZE, _runner
    )
    return selected_id, screen


def _confirm_exit_secondary(screen):
    def _runner(screen):
        clock = pygame.time.Clock()
        selected = 1
        options = ["No", "Si"]
        repeater = MenuArrowRepeater()
        while True:
            render_lines = (
                ["Confirmar salida", "Deseas cerrar el HUD?"]
                + options
                + ["Flechas + Enter | Esc"]
            )
            font, line_gap = build_responsive_font(
                screen,
                render_lines,
                base_size=30,
                min_size=14,
                max_size=34,
                base_resolution=(420, 220),
            )
            screen.fill((0, 0, 0))
            title_y = max(28, line_gap)
            draw_centered_text(screen, font, "Confirmar salida", y=title_y)
            draw_centered_text(
                screen, font, "Deseas cerrar el HUD?", y=title_y + line_gap
            )
            for index, option in enumerate(options):
                prefix = ">" if index == selected else " "
                draw_centered_text(
                    screen,
                    font,
                    f"{prefix} {option}",
                    y=title_y + line_gap * (3 + index),
                )
            draw_centered_text(
                screen,
                font,
                "Flechas + Enter | Esc",
                y=screen.get_height() - max(20, line_gap),
            )
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in (
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ):
                        dnav = repeater.consume_keydown(event)
                        if dnav is not None:
                            selected = (selected + dnav) % len(options)
                    else:
                        repeater.reset()
                        if event.key == pygame.K_ESCAPE:
                            return False
                        elif event.key == pygame.K_RETURN:
                            return options[selected] == "Si"
            d2 = repeater.tick_held()
            if d2 is not None:
                selected = (selected + d2) % len(options)
            clock.tick(FPS)

    confirmed, screen = _run_secondary_selector(
        screen, "Confirmar salida", CONFIRM_WINDOW_SIZE, _runner
    )
    return confirmed, screen


def _confirm_keyboard_remap_secondary(screen):
    def _runner(screen):
        clock = pygame.time.Clock()
        selected = 0
        options = ["No", "Si", "Cancelar y volver"]
        repeater = MenuArrowRepeater()
        while True:
            render_lines = (
                ["Modo teclado", "Quieres remapear teclas?"]
                + options
                + ["Flechas + Enter | Esc"]
            )
            font, line_gap = build_responsive_font(
                screen,
                render_lines,
                base_size=30,
                min_size=14,
                max_size=34,
                base_resolution=(420, 220),
            )
            screen.fill((0, 0, 0))
            title_y = max(28, line_gap)
            draw_centered_text(screen, font, "Modo teclado", y=title_y)
            draw_centered_text(
                screen, font, "Quieres remapear teclas?", y=title_y + line_gap
            )
            for index, option in enumerate(options):
                prefix = ">" if index == selected else " "
                draw_centered_text(
                    screen,
                    font,
                    f"{prefix} {option}",
                    y=title_y + line_gap * (3 + index),
                )
            draw_centered_text(
                screen,
                font,
                "Flechas + Enter | Esc",
                y=screen.get_height() - max(20, line_gap),
            )
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in (
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ):
                        dnav = repeater.consume_keydown(event)
                        if dnav is not None:
                            selected = (selected + dnav) % len(options)
                    else:
                        repeater.reset()
                        if event.key == pygame.K_ESCAPE:
                            return "cancelar"
                        elif event.key == pygame.K_RETURN:
                            if options[selected] == "Si":
                                return "si"
                            if options[selected] == "No":
                                return "no"
                            return "cancelar"
            d2 = repeater.tick_held()
            if d2 is not None:
                selected = (selected + d2) % len(options)
            clock.tick(FPS)

    confirmed, screen = _run_secondary_selector(
        screen, "Remapeo teclado", CONFIRM_WINDOW_SIZE, _runner
    )
    return confirmed, screen


def _choose_keyboard_device_secondary(screen, current_path):
    def _runner(screen):
        clock = pygame.time.Clock()
        devices = list_keyboard_devices_by_capabilities()
        options = [("Ninguno (solo con foco)", None)]
        for device in devices:
            options.append((f"{device.name} | {device.path}", device.path))
        for device in devices:
            device.close()

        selected = 0
        for index, option in enumerate(options):
            if option[1] == current_path:
                selected = index
                break

        repeater = MenuArrowRepeater()
        while True:
            lines_for_fit = (
                ["Teclado global (sin foco)"]
                + [label for label, _ in options[:6]]
                + ["Flechas + Enter | Esc"]
            )
            font, line_gap = build_responsive_font(
                screen,
                lines_for_fit,
                base_size=28,
                min_size=14,
                max_size=34,
                base_resolution=SELECTOR_WINDOW_SIZE,
                max_height_ratio=0.82,
            )
            screen.fill((0, 0, 0))
            title_y = max(28, line_gap)
            draw_centered_text(screen, font, "Teclado global (sin foco)", y=title_y)

            start_index = max(0, selected - 2)
            end_index = min(len(options), start_index + 5)
            visible = options[start_index:end_index]
            start_y = title_y + line_gap
            for visible_index, (label, _) in enumerate(visible):
                option_index = start_index + visible_index
                prefix = ">" if option_index == selected else " "
                trimmed = fit_text_to_width(font, label, int(screen.get_width() * 0.90))
                draw_centered_text(
                    screen,
                    font,
                    f"{prefix} {trimmed}",
                    y=start_y + visible_index * line_gap,
                )

            draw_centered_text(
                screen,
                font,
                "Flechas + Enter | Esc",
                y=screen.get_height() - max(20, line_gap),
            )
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "cancelar", current_path
                if event.type == pygame.KEYDOWN:
                    if event.key in (
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ):
                        dnav = repeater.consume_keydown(event)
                        if dnav is not None:
                            selected = (selected + dnav) % len(options)
                    else:
                        repeater.reset()
                        if event.key == pygame.K_ESCAPE:
                            return "cancelar", current_path
                        elif event.key == pygame.K_RETURN:
                            return "ok", options[selected][1]
            d2 = repeater.tick_held()
            if d2 is not None:
                selected = (selected + d2) % len(options)
            clock.tick(FPS)

    result, screen = _run_secondary_selector(
        screen, "Teclado global", SELECTOR_WINDOW_SIZE, _runner
    )
    return result, screen


_MAIN_MENU_ACTION_BY_INDEX = ["iniciar", "configurar", "salir"]


def _handle_main_menu_key(event, selected, options_len, repeater=None):
	key = event.key
	if repeater is not None and event.type == pygame.KEYDOWN:
		if key not in (
			pygame.K_UP,
			pygame.K_DOWN,
			pygame.K_LEFT,
			pygame.K_RIGHT,
		):
			repeater.reset()
	if repeater is not None:
		if key in (
			pygame.K_UP,
			pygame.K_DOWN,
			pygame.K_LEFT,
			pygame.K_RIGHT,
		):
			d = repeater.consume_keydown(event)
			if d is not None:
				return (selected + d) % options_len, None
			return selected, None
	if key in (pygame.K_UP, pygame.K_LEFT):
		return (selected - 1) % options_len, None
	if key in (pygame.K_DOWN, pygame.K_RIGHT):
		return (selected + 1) % options_len, None
	if key == pygame.K_ESCAPE:
		return selected, "salir"
	if (
		not getattr(event, "repeat", False)
		and key == pygame.K_EQUALS
		and selected == 0
		and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
	):
		_launch_easteregg_instance()
		return selected, None
	if key == pygame.K_RETURN:
		action = _MAIN_MENU_ACTION_BY_INDEX[min(selected, len(_MAIN_MENU_ACTION_BY_INDEX) - 1)]
		return selected, action
	return selected, None


def _draw_main_menu(screen, options, selected):
    """Dibuja el menú una vez. Render persistente, no en bucle."""
    _debug_menu("_draw_main_menu")
    lines = (
        [WINDOW_CAPTION_APP]
        + options
        + ["Flechas + Enter"]
        + ["= en Iniciar HUD: nueva instancia"]
    )
    font, line_gap = build_responsive_font(
        screen,
        lines,
        base_size=30,
        min_size=14,
        max_size=36,
        base_resolution=(screen.get_width(), screen.get_height()),
        max_height_ratio=0.88,
    )
    screen.fill((0, 0, 0))
    title_y = max(28, line_gap)
    base_y = title_y + line_gap
    for index, option in enumerate(options):
        prefix = ">" if index == selected else " "
        draw_centered_text(
            screen, font, f"{prefix} {option}", y=base_y + index * line_gap
        )
    draw_centered_text(screen, font, WINDOW_CAPTION_APP, y=title_y)
    draw_centered_text(
        screen, font, "Flechas + Enter", y=base_y + len(options) * line_gap
    )
    if selected == 0 and EASTEREGG_ENABLE_MULTI_INSTANCE:
        draw_centered_text(
            screen,
            font,
            "=: instancia extra",
            y=screen.get_height() - max(18, line_gap),
        )
    pygame.display.flip()


def _process_main_menu_event(event, selected, len_options, ignore_videoresize, repeater=None):
    """Procesa un evento del menu principal. Retorna (new_selected, action, pending_resize)."""
    _debug_menu(
        f"evento {pygame.event.event_name(event.type) if hasattr(pygame.event, 'event_name') else event.type} ({getattr(event, 'w', '')}x{getattr(event, 'h', '')})"
    )
    if event.type == pygame.QUIT:
        _debug_menu("show_main_menu FIN -> salir")
        return selected, "salir", None
    if event.type == pygame.VIDEORESIZE:
        if ignore_videoresize:
            _debug_report_videoresize_stats()
            return selected, None, None
        _debug_count_videoresize()
        return selected, None, (event.w, event.h)
    if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
        new_selected, action = _handle_main_menu_key(event, selected, len_options, repeater)
        if action:
            _debug_menu(f"show_main_menu FIN -> {action}")
        return new_selected, action, None
    return selected, None, None


def _apply_main_menu_resize(screen, pending_resize, ignore_videoresize):
    """Aplica resize en el menu principal si corresponde. Retorna la pantalla (posiblemente nueva)."""
    if pending_resize is None or ignore_videoresize:
        return screen
    now_ms = time.time() * 1000
    if now_ms - get_last_set_mode_time_ms() < VIDEORESIZE_COOLDOWN_MS:
        return screen
    new_w = max(MIN_WINDOW_WIDTH, pending_resize[0])
    new_h = max(MIN_WINDOW_HEIGHT, pending_resize[1])
    cur_w, cur_h = screen.get_size()
    if abs(new_w - cur_w) <= VIDEORESIZE_TOLERANCE_PX and abs(new_h - cur_h) <= VIDEORESIZE_TOLERANCE_PX:
        return screen
    screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
    track_set_mode()
    _debug_count_set_mode()
    return screen


def show_main_menu(screen, profile_data=None):
    _debug_menu("show_main_menu INICIO")
    options = ["Iniciar HUD", "Configuración", "Salir"]
    selected = 0
    ignore_videoresize = (
        os.environ.get("JOYSTICK_IGNORE_VIDEORESIZE") == "1"
        or (profile_data or {}).get("ignore_videoresize", False)
    )
    repeater = MenuArrowRepeater()
    clock = pygame.time.Clock()

    while True:
        events = pygame.event.get()
        pending_resize = None
        for event in events:
            new_selected, action, pr = _process_main_menu_event(
                event, selected, len(options), ignore_videoresize, repeater
            )
            selected = new_selected
            if pr is not None:
                pending_resize = pr
            if action:
                return action
        dnav = repeater.tick_held()
        if dnav is not None:
            selected = (selected + dnav) % len(options)
        screen = _apply_main_menu_resize(screen, pending_resize, ignore_videoresize)
        _debug_report_videoresize_stats()
        _draw_main_menu(screen, options, selected)
        time.sleep(0.005)
        clock.tick(60)


class AppContext:
    """Contexto compartido del bucle principal (perfil, resize y acción del menú)."""

    def __init__(self, profile_data):
        self.profile_data = profile_data if profile_data is not None else {}
        self.pending_menu_resize = None
        self.menu_action = None

    def ignore_videoresize_menu(self):
        return (
            os.environ.get("JOYSTICK_IGNORE_VIDEORESIZE") == "1"
            or self.profile_data.get("ignore_videoresize", False)
        )


class MainMenuState(BaseState):
    """Menú principal (Iniciar / Configuración / Salir) como estado en la misma ventana."""

    def __init__(self):
        self.options = ["Iniciar HUD", "Configuración", "Salir"]
        self.selected = 0
        self._arrow_repeater = MenuArrowRepeater()

    def enter(self, ctx):
        self.selected = 0
        self._arrow_repeater = MenuArrowRepeater()
        _debug_menu("MainMenuState enter")

    def handle_events(self, ctx, events):
        ctx.menu_action = None
        ctx.pending_menu_resize = None
        ignore = ctx.ignore_videoresize_menu()
        for event in events:
            new_selected, action, pr = _process_main_menu_event(
                event, self.selected, len(self.options), ignore, self._arrow_repeater
            )
            self.selected = new_selected
            if pr is not None:
                ctx.pending_menu_resize = pr
            if action:
                ctx.menu_action = action
        dnav = self._arrow_repeater.tick_held()
        if dnav is not None:
            self.selected = (self.selected + dnav) % len(self.options)
        return None

    def draw(self, ctx, screen):
        _draw_main_menu(screen, self.options, self.selected)


def _open_config_secondary_window(screen, profile_data):
    updated = open_profile_config_menu(screen, profile_data)
    return updated, screen


def _run_hud_setup_interactive(profile, profile_data, screen):
    button_count, screen = _run_secondary_selector(
        screen,
        "Formato de botones",
        SELECTOR_WINDOW_SIZE,
        lambda s: choose_button_format(s, profile["button_count"]),
    )
    if button_count is None:
        return None
    input_mode = None
    selected_device_path = profile.get("preferred_joystick_path")
    wants_keyboard_remap = False
    while input_mode is None:
        mode_choice, screen = _run_secondary_selector(
            screen,
            "Modo de entrada",
            SELECTOR_WINDOW_SIZE,
            lambda s: choose_input_mode(s, profile["input_mode"]),
        )
        if mode_choice is None:
            return None
        if mode_choice in ["teclado", "hitbox", "mixbox"]:
            keyboard_action, screen = _confirm_keyboard_remap_secondary(screen)
            if keyboard_action == "cancelar":
                continue
            select_status, screen = _choose_keyboard_device_secondary(
                screen, profile.get("preferred_keyboard_path")
            )
            if select_status[0] == "cancelar":
                continue
            profile["preferred_keyboard_path"] = select_status[1]
            wants_keyboard_remap = keyboard_action == "si"
            input_mode = mode_choice
            break
        diagnostic, screen = _run_secondary_selector(
            screen,
            "Diagnostico joystick",
            MAPPER_WINDOW_SIZE,
            lambda s: run_joystick_diagnostic(
                s,
                button_count,
                window_mode=profile_data.get("window_mode", "floating_hint"),
                controller_style=profile.get("controller_style", "default"),
            ),
        )
        if diagnostic.get("status") == "back_to_input":
            continue
        selected_device_path = diagnostic.get("device_path")
        if diagnostic.get("status") == "mapped":
            profile["joystick_bindings"] = diagnostic.get("bindings", {})
            profile["joystick_bindings_style"] = profile.get(
                "controller_style", "default"
            )
        input_mode = "joystick"
    return (
        button_count,
        input_mode,
        selected_device_path,
        wants_keyboard_remap,
        screen,
    )


def _run_hud_setup_non_interactive(profile):
    return (
        profile.get("button_count", 6),
        profile.get("input_mode", "teclado"),
        profile.get("preferred_joystick_path"),
        False,
        None,
    )


def _keyboard_bindings_incomplete(profile, button_count):
    kb = profile.get("key_bindings") or {}
    need = (
        ["Arriba", "Abajo", "Izquierda", "Derecha"]
        + get_button_labels(button_count)
        + ["SELECT", "START"]
    )
    return any(k not in kb for k in need)


def _joystick_bindings_need_mapping(profile, button_count):
    jb = profile.get("joystick_bindings") or {}
    for lbl in get_button_labels(button_count) + ["SELECT", "START"]:
        if jb.get(lbl) is not None:
            return False
    return True


def _run_keyboard_mapping_flow(screen, profile, button_count, interactive_setup):
    if _keyboard_bindings_incomplete(profile, button_count):
        profile["key_bindings"] = {}
    if not profile["key_bindings"]:
        if not interactive_setup:
            print("[WARN] Perfil sin key_bindings en modo no interactivo.")
            return False, screen
        fmt = get_active_bindings_format_key(profile)
        im = profile.get("input_mode", "teclado")
        pid = profile["id"]
        mapped, new_screen = _run_secondary_selector(
            screen,
            "Mapeo teclado",
            MAPPER_WINDOW_SIZE,
            lambda s: map_keys(s, button_count, pid, fmt, im),
        )
        if mapped:
            profile["key_bindings"] = mapped
        screen = new_screen
    return True, screen


def _run_joystick_mapping_flow(screen, profile, button_count, selected_device_path):
    if profile.get("joystick_bindings_style") != profile.get(
        "controller_style", "default"
    ):
        profile["joystick_bindings"] = {}
    if _joystick_bindings_need_mapping(profile, button_count):
        mapped, new_screen = _run_secondary_selector(
            screen,
            "Mapeo joystick",
            MAPPER_WINDOW_SIZE,
            lambda s: map_joystick_buttons(
                s,
                button_count,
                show_error=False,
                device_path=selected_device_path,
                controller_style=profile.get("controller_style", "default"),
                profile_id=profile["id"],
                format_key=get_active_bindings_format_key(profile),
            ),
        )
        if not mapped:
            return False, screen
        profile["joystick_bindings"] = mapped
        profile["joystick_bindings_style"] = profile.get("controller_style", "default")
        screen = new_screen
    return True, screen


def _handle_hud_return_key(keys, training_state):
    """Maneja tecla RETURN en HUD: Backspace+Enter lanza training, Enter solo hace playback."""
    if keys[pygame.K_BACKSPACE]:
        if has_sequence(training_state):
            _launch_training_window(sequence_to_dict(training_state))
        return
    if training_state["status"] == "recording":
        stop_recording(training_state)
    if has_sequence(training_state):
        start_playback(training_state)


def _handle_hud_tab_key(training_state):
    """Alterna grabacion con TAB."""
    if training_state["status"] == "recording":
        stop_recording(training_state)
    else:
        start_recording(training_state)


def _process_hud_keydown(event, keys, training_state):
    """Procesa KEYDOWN del bucle HUD. Retorna (running, training_state)."""
    key = event.key
    if key == pygame.K_ESCAPE:
        return False, training_state
    if (
        not getattr(event, "repeat", False)
        and key == pygame.K_EQUALS
        and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
    ):
        _launch_easteregg_instance()
        return True, training_state
    if key == pygame.K_TAB:
        _handle_hud_tab_key(training_state)
        return True, training_state
    if key == pygame.K_RETURN:
        _handle_hud_return_key(keys, training_state)
        return True, training_state
    if key == pygame.K_BACKSPACE and not keys[pygame.K_RETURN]:
        clear_sequence(training_state)
    return True, training_state


def _process_hud_events(events, keys, training_state):
    """Procesa eventos del bucle HUD. Retorna (running, pending_resize)."""
    running = True
    pending_resize = None
    for event in events:
        emit_hook(
            "hud_events_polled",
            {"type": int(event.type), "name": pygame.event.event_name(event.type)},
        )
        if event.type == pygame.VIDEORESIZE:
            _debug_count_videoresize()
            pending_resize = (event.w, event.h)
        elif event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            emit_hook(
                "hud_event_keydown",
                {"key": int(event.key), "repeat": bool(getattr(event, "repeat", False))},
            )
            running, training_state = _process_hud_keydown(event, keys, training_state)
            if not running:
                break
    return running, pending_resize


def _apply_hud_resize(screen, pending_resize, ignore_videoresize):
    """Aplica resize de ventana si corresponde. Retorna la pantalla (posiblemente nueva)."""
    if pending_resize is None or ignore_videoresize:
        return screen
    now_ms = time.time() * 1000
    if now_ms - get_last_set_mode_time_ms() < VIDEORESIZE_COOLDOWN_MS:
        return screen
    new_w = max(MIN_WINDOW_WIDTH, pending_resize[0])
    new_h = max(MIN_WINDOW_HEIGHT, pending_resize[1])
    cur_w, cur_h = screen.get_size()
    if abs(new_w - cur_w) <= VIDEORESIZE_TOLERANCE_PX and abs(new_h - cur_h) <= VIDEORESIZE_TOLERANCE_PX:
        return screen
    screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
    track_set_mode()
    _debug_count_set_mode()
    return screen


def _hud_layout_key_for_mode(input_mode):
    if input_mode == "mixbox":
        return "mixbox"
    if input_mode == "hitbox":
        return "hitbox"
    return "stick"


def _hud_frame_render_context(screen, input_state, profile, input_mode, button_count):
    """Snapshot thread-safe + offsets de layout para un frame HUD."""
    input_snap = snapshot_input_state(input_state)
    layout_key = _hud_layout_key_for_mode(input_mode)
    layout_off = resolve_hud_layout_offsets(
        profile,
        screen.get_width(),
        screen.get_height(),
        layout_key,
        button_count,
    )
    return input_snap, layout_off


def _run_hud_main_loop(
    screen,
    input_state,
    button_count,
    profile_data,
    input_mode,
    selected_device_path,
    profile,
    force_tournament,
):
    labels = get_button_labels(button_count)
    tournament_mode = bool(force_tournament)
    resolved_icons = resolve_icons_map(profile["id"], button_count)
    load_icons(button_count, resolved_icons, enable_icons=not tournament_mode)
    load_system_icons(profile)
    set_stick_color(profile["joystick_color"])
    set_stick_colors(
        profile.get("joystick_knob_color", profile["joystick_color"]),
        profile.get("joystick_bar_color", [0, 0, 0]),
        profile.get("joystick_ring_color", [255, 255, 255]),
    )
    set_button_colors(
        profile.get("button_color_inactive", [80, 80, 80]),
        profile.get("button_color_active", [255, 0, 0]),
    )
    set_controller_style(profile.get("controller_style", "default"))
    set_render_mode("tournament" if tournament_mode else "normal")
    layout = (
        "mixbox"
        if input_mode == "mixbox"
        else ("hitbox" if input_mode == "hitbox" else "stick")
    )
    set_input_layout(layout)
    set_hitbox_alt_layout(profile.get("hitbox_alt_layout", False))
    history_cfg = profile_data.get("extensions", {})
    history_max_events = history_cfg.get("input_history_max_events", 1000)
    input_history = InputHistory(max_events=history_max_events)

    def _on_input_state_update(source, state_snapshot):
        changes = input_history.record_snapshot(
            state_snapshot,
            source=source,
            player_id="p1",
        )
        if not changes:
            return
        for change in changes:
            emit_hook("input_state_updated", {"change": change})

    emit_hook(
        "session_start",
        {
            "button_count": button_count,
            "input_mode": input_mode,
            "tournament_mode": bool(tournament_mode),
        },
    )
    threading.Thread(
        target=start_input_listener,
        args=(
            input_mode,
            button_count,
            input_state,
            selected_device_path,
            profile.get("preferred_keyboard_path"),
            _on_input_state_update,
            bool(profile.get("layout_four_variant_4a")),
        ),
        daemon=True,
    ).start()
    clock = pygame.time.Clock()
    running = True
    bg = get_background_color(profile_data.get("capture_mode", "normal"))
    target_fps = TOURNAMENT_FPS if tournament_mode else FPS
    training_state = create_training_state()
    ignore_videoresize = (
        os.environ.get("JOYSTICK_IGNORE_VIDEORESIZE") == "1"
        or profile_data.get("ignore_videoresize", False)
    )
    while running:
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        running, pending_resize = _process_hud_events(events, keys, training_state)
        input_snap, layout_off = _hud_frame_render_context(
            screen, input_state, profile, input_mode, button_count
        )
        snapshot_if_recording(training_state, input_snap)
        if training_state["status"] == "playing":
            update_playback(training_state, input_snap)
        screen.fill(bg)
        emit_hook(
            "hud_frame_pre_render",
            {
                "input_state_snapshot": input_snap,
                "layout_offsets": layout_off,
            },
        )
        draw_hud(screen, input_snap, button_count, layout_offsets=layout_off)
        emit_hook(
            "hud_frame_post_render",
            {"fps_target": target_fps, "history_size": len(input_history.events)},
        )
        pygame.display.flip()
        screen = _apply_hud_resize(screen, pending_resize, ignore_videoresize)
        _debug_report_videoresize_stats()
        time.sleep(0.005)
        clock.tick(target_fps)
    emit_hook(
        "session_end",
        {
            "button_count": button_count,
            "input_mode": input_mode,
            "history": input_history.to_dict(),
        },
    )


def _run_hud_setup(profile, profile_data, interactive_setup, screen):
    """Ejecuta setup interactivo o no. Retorna (button_count, input_mode, selected_device_path, wants_keyboard_remap, screen) o None."""
    if interactive_setup:
        result = _run_hud_setup_interactive(profile, profile_data, screen)
        if result is None:
            return None
        bc, im, sdp, wkr, setup_screen = result
        return bc, im, sdp, wkr, setup_screen
    bc, im, sdp, wkr, _ = _run_hud_setup_non_interactive(profile)
    return bc, im, sdp, wkr, None


def _apply_session_profile(profile, button_count, input_mode, selected_device_path, labels, wants_keyboard_remap):
    """Aplica valores de setup al perfil activo."""
    profile["button_count"] = button_count
    if button_count != 4:
        profile["layout_four_variant_4a"] = False
    profile["input_mode"] = input_mode
    profile["preferred_joystick_path"] = selected_device_path
    profile["button_icons"] = {lbl: profile["button_icons"].get(lbl) for lbl in labels}
    if profile["joystick_bindings"] and any(lbl not in profile["joystick_bindings"] for lbl in labels):
        profile["joystick_bindings"] = {}
    if input_mode in ["teclado", "hitbox", "mixbox"] and wants_keyboard_remap:
        profile["key_bindings"] = {}


def _run_input_mapping_flows(screen, profile, button_count, input_mode, selected_device_path, interactive_setup):
    """Ejecuta flujos de mapeo segun modo de entrada. Retorna (ok, screen)."""
    if input_mode in ["teclado", "hitbox", "mixbox"]:
        ok, screen = _run_keyboard_mapping_flow(screen, profile, button_count, interactive_setup)
        if not ok:
            return False, screen
    if input_mode == "joystick":
        ok, screen = _run_joystick_mapping_flow(screen, profile, button_count, selected_device_path)
        if not ok:
            return False, screen
    return True, screen


def run_hud_session(
    screen, profile_data, interactive_setup=True, force_tournament=False
):
    set_extensions_enabled(
        profile_data.get("extensions", {}).get("plugin_standby_enabled", True)
    )
    profile = get_active_profile(profile_data)
    setup_result = _run_hud_setup(profile, profile_data, interactive_setup, screen)
    if setup_result is None:
        return False
    button_count, input_mode, selected_device_path, wants_keyboard_remap, setup_screen = setup_result
    if setup_screen is not None:
        screen = setup_screen

    labels = get_button_labels(button_count)
    _apply_session_profile(profile, button_count, input_mode, selected_device_path, labels, wants_keyboard_remap)

    ok, screen = _run_input_mapping_flows(
        screen, profile, button_count, input_mode, selected_device_path, interactive_setup
    )
    if not ok:
        return False

    sync_active_profile_to_legacy_files(profile_data)
    save_profiles_data(profile_data)
    input_state = create_input_state(len(labels))
    bind_input_state_lock(input_state)
    _run_hud_main_loop(
        screen,
        input_state,
        button_count,
        profile_data,
        input_mode,
        selected_device_path,
        profile,
        force_tournament,
    )
    return True


def main():
    if "--do-reset-data" in sys.argv[1:]:
        return _do_reset_data()
    if "--reset-data" in sys.argv[1:]:
        return _run_reset_data_confirmation()
    if not _preflight_startup():
        return
    global _current_window_mode
    pygame.init()
    os.environ["SDL_VIDEO_WINDOW_POS"] = "100,100"
    _current_window_mode = "floating_hint"
    # Una sola superficie al tamaño del HUD: evita set_mode menú↔HUD y mantiene foco/captura (p. ej. OBS).
    screen = _set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_CAPTION_APP)

    profile_data = load_profiles_data()
    profile_data = run_backup_welcome_if_needed(screen, profile_data)
    profile_data = run_first_run_wizard_if_needed(screen, profile_data)
    _current_window_mode = (
        "normal"
        if os.environ.get("JOYSTICK_WINDOW_MODE_NORMAL") == "1"
        else profile_data.get("window_mode", "floating_hint")
    )
    set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))

    ctx = AppContext(profile_data)
    sm = StateManager(MainMenuState(), ctx)
    clock = pygame.time.Clock()

    while True:
        ctx.profile_data = profile_data
        _current_window_mode = (
            "normal"
            if os.environ.get("JOYSTICK_WINDOW_MODE_NORMAL") == "1"
            else profile_data.get("window_mode", "floating_hint")
        )
        set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))

        events = pygame.event.get()
        sm.handle_events(events)
        action = ctx.menu_action
        _debug_menu(f"main loop action={action!r}")

        if action == "salir":
            confirmed, screen = _confirm_exit_secondary(screen)
            if confirmed:
                break
            _debug_menu("main loop continue (salir cancelado)")
            continue
        if action == "configurar":
            updated, screen = _open_config_secondary_window(screen, profile_data)
            if updated:
                profile_data = updated
                save_profiles_data(profile_data)
                set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
            _debug_menu("main loop continue (configurar)")
            continue
        if action == "iniciar":
            run_hud_session(screen, profile_data)
            continue

        screen = _apply_main_menu_resize(
            screen, ctx.pending_menu_resize, ctx.ignore_videoresize_menu()
        )
        _debug_report_videoresize_stats()
        sm.update(0.016)
        sm.draw(screen)
        pygame.display.flip()
        time.sleep(0.005)
        clock.tick(60)

    pygame.quit()
    sys.exit()


def _append_reset_log(message):
    ensure_contract_dirs()
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    with open(RESET_LOG_PATH, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | reset | {message}\n")


def _do_reset_data():
    try:
        from datetime import datetime

        if os.path.isdir(USER_DIR):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_dir = os.path.join(
                tempfile.gettempdir(), f"joystick_overlay_pre_reset_{ts}"
            )
            os.makedirs(pre_dir, exist_ok=True)
            for fname in (
                "reset.log",
                "profiles_index.json",
                "update.log",
                ".data_version",
            ):
                fp = os.path.join(USER_DIR, fname)
                if os.path.isfile(fp):
                    shutil.copy2(fp, os.path.join(pre_dir, fname))
            shutil.rmtree(USER_DIR)
        ensure_contract_dirs()
        write_data_version(CURRENT_DATA_VERSION)
        _append_reset_log("SUCCESS user dir reset")
        print("Reset de datos completado (canon bajo proyecto).")
        print(f"Espejo de perfiles en XDG no borrado: {BACKUP_PROFILES_ROOT}")
        print(
            "Si hubo pre-respaldos de reset, buscar carpetas joystick_overlay_pre_reset_* en el directorio temporal del sistema."
        )
        return
    except Exception as error:
        _append_reset_log(f"ERROR {error}")
        print(f"No se pudo resetear datos: {error}")


def _run_reset_data_confirmation():
    print(f"Se borrará el directorio de datos del proyecto: {USER_DIR}")
    print("(Pre-respaldado fuera del repo: joystick_overlay_pre_reset_* en el tmp del sistema.)")
    print(f"No se borra el espejo XDG de perfiles: {BACKUP_PROFILES_ROOT}")
    confirm = input("Confirmar reset de datos? (s/n): ").strip().lower()
    if confirm not in ("s", "si"):
        print("Reset cancelado.")
        return
    args = [sys.executable, os.path.abspath(__file__), "--do-reset-data"]
    subprocess.run(args, check=False, cwd=os.path.dirname(__file__))


def _preflight_startup():
    ensure_contract_dirs()
    assets_version = get_assets_version()
    if not assets_version:
        print(f"[ERR] assets inválidos: falta {ASSETS_VERSION_PATH}")
        return False
    runtime_version = get_runtime_version()
    if not runtime_version:
        print(f"[ERR] runtime inválido: falta {RUNTIME_VERSION_PATH}")
        return False
    data_version_raw = get_data_version(default_version="0")
    try:
        data_version = int(data_version_raw)
    except Exception:
        data_version = 0
    if data_version < CURRENT_DATA_VERSION:
        result = migrate_if_needed()
        print(f"[INFO] Migración de datos: {result}")
        clear_assets_cache()
    elif data_version > CURRENT_DATA_VERSION:
        print(
            f"[ERR] data_version ({data_version}) mayor que soportado ({CURRENT_DATA_VERSION})."
        )
        return False
    if runtime_version != os.environ.get(
        "JOYSTICK_EXPECTED_RUNTIME_VERSION", runtime_version
    ):
        print("[WARN] .joystick_version no coincide con runtime esperado; continuando.")
    if not os.path.isdir(PROFILES_DIR):
        ensure_contract_dirs()
    return True


if __name__ == "__main__":
    main()
