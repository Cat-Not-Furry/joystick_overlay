# main.py

# ---Archivo principal ---

import os
os.environ.setdefault("SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR", "0")

import pygame
import threading
import sys
import subprocess
import tempfile
import json
import time


def _debug_menu(msg):
    if os.environ.get("HUD_DEBUG_MENU") == "1":
        ts = (
            time.strftime("%H:%M:%S", time.localtime())
            + f".{int((time.time() % 1) * 1000):03d}"
        )
        print(f"[HUD_DEBUG] {ts} | {msg}")


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
    if os.environ.get("HUD_DEBUG_MENU") != "1":
        return
    global _debug_videoresize_count, _debug_set_mode_count, _debug_stats_last_sec
    now = time.time()
    if now - _debug_stats_last_sec >= 1.0 and (_debug_videoresize_count > 0 or _debug_set_mode_count > 0):
        elapsed = now - _debug_stats_last_sec
        vr_per_sec = _debug_videoresize_count / elapsed
        sm_per_sec = _debug_set_mode_count / elapsed
        print(f"[HUD_DEBUG] stats | VIDEORESIZE/s: {vr_per_sec:.1f} | set_mode/s: {sm_per_sec:.1f}")
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
    get_button_labels,
    get_background_color,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    VIDEORESIZE_COOLDOWN_MS,
    VIDEORESIZE_TOLERANCE_PX,
    EASTEREGG_ENABLE_MULTI_INSTANCE,
    EASTEREGG_MULTI_INSTANCE_KEY,
    EASTEREGG_MAX_INSTANCES,
)
from render import choose_button_format, choose_input_mode, open_profile_config_menu
from render import draw_hud, load_icons, set_stick_color, set_stick_colors, set_button_colors
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
from utils import (
    draw_centered_text,
    build_responsive_font,
    fit_text_to_width,
    open_secondary_window,
    restore_primary_window,
    list_keyboard_devices_by_capabilities,
    set_ui_font_family,
    track_set_mode,
    get_last_set_mode_time_ms,
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
        if "python" in cmdline and "main.py" in cmdline and "hud_overlay" in cmdline:
            count += 1
    return count


def _launch_training_window(sequence_data):
    """Lanza ventana de entrenamiento independiente con la secuencia."""
    fd, path = tempfile.mkstemp(suffix=".json", prefix="hud_training_")
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


def _run_secondary_selector(title, size, runner):
    window_mode = "floating_hint"
    try:
        window_mode = _current_window_mode
    except NameError:
        pass
    secondary, primary_size = open_secondary_window(
        title, size=size, window_mode=window_mode
    )
    result = runner(secondary)
    primary = restore_primary_window(
        primary_size, window_mode=window_mode, title="Arcade HUD Overlay"
    )
    return result, primary


def select_profile_secondary(profile_data, title="Selecciona perfil"):
    def _runner(screen):
        clock = pygame.time.Clock()
        profiles = profile_data["profiles"]
        selected = 0
        for index, profile in enumerate(profiles):
            if profile["id"] == profile_data.get("active_profile"):
                selected = index
                break

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
                    if event.key in (pygame.K_UP, pygame.K_LEFT):
                        selected = (selected - 1) % len(profiles)
                    elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                        selected = (selected + 1) % len(profiles)
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_RETURN:
                        return profiles[selected]["id"]
            clock.tick(FPS)

    selected_id, screen = _run_secondary_selector(title, SELECTOR_WINDOW_SIZE, _runner)
    return selected_id, screen


def _confirm_exit_secondary():
    def _runner(screen):
        clock = pygame.time.Clock()
        selected = 1
        options = ["No", "Si"]
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
                        pygame.K_LEFT,
                        pygame.K_DOWN,
                        pygame.K_RIGHT,
                    ):
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_RETURN:
                        return options[selected] == "Si"
            clock.tick(FPS)

    confirmed, restored = _run_secondary_selector(
        "Confirmar salida", CONFIRM_WINDOW_SIZE, _runner
    )
    return confirmed, restored


def _confirm_keyboard_remap_secondary():
    def _runner(screen):
        clock = pygame.time.Clock()
        selected = 0
        options = ["No", "Si", "Cancelar y volver"]
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
                        pygame.K_LEFT,
                        pygame.K_DOWN,
                        pygame.K_RIGHT,
                    ):
                        if event.key in (pygame.K_UP, pygame.K_LEFT):
                            selected = (selected - 1) % len(options)
                        else:
                            selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_ESCAPE:
                        return "cancelar"
                    elif event.key == pygame.K_RETURN:
                        if options[selected] == "Si":
                            return "si"
                        if options[selected] == "No":
                            return "no"
                        return "cancelar"
            clock.tick(FPS)

    confirmed, restored = _run_secondary_selector(
        "Remapeo teclado", CONFIRM_WINDOW_SIZE, _runner
    )
    return confirmed, restored


def _choose_keyboard_device_secondary(current_path):
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
                    if event.key in (pygame.K_UP, pygame.K_LEFT):
                        selected = (selected - 1) % len(options)
                    elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_ESCAPE:
                        return "cancelar", current_path
                    elif event.key == pygame.K_RETURN:
                        return "ok", options[selected][1]
            clock.tick(FPS)

    result, restored = _run_secondary_selector(
        "Teclado global", SELECTOR_WINDOW_SIZE, _runner
    )
    return result, restored


def _handle_main_menu_key(event, selected, options_len):
    if event.key in (pygame.K_UP, pygame.K_LEFT):
        return (selected - 1) % options_len, None
    if event.key in (pygame.K_DOWN, pygame.K_RIGHT):
        return (selected + 1) % options_len, None
    if event.key == pygame.K_ESCAPE:
        return selected, "salir"
    if (
        not getattr(event, "repeat", False)
        and event.key == pygame.K_EQUALS
        and selected == 0
        and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
    ):
        _launch_easteregg_instance()
        return selected, None
    if event.key == pygame.K_RETURN:
        if selected == 0:
            return selected, "iniciar"
        if selected == 1:
            return selected, "configurar"
        return selected, "salir"
    return selected, None


def _draw_main_menu(screen, options, selected):
    """Dibuja el menú una vez. Render persistente, no en bucle."""
    _debug_menu("_draw_main_menu")
    lines = (
        ["HUD Overlay"]
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
        base_resolution=(MENU_WIDTH, MENU_HEIGHT),
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
    draw_centered_text(screen, font, "HUD Overlay", y=title_y)
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


def show_main_menu(screen, profile_data=None):
    _debug_menu("show_main_menu INICIO")
    options = ["Iniciar HUD", "Configurar perfiles", "Salir"]
    selected = 0
    _draw_main_menu(screen, options, selected)
    ignore_videoresize = (
        os.environ.get("HUD_IGNORE_VIDEORESIZE") == "1"
        or (profile_data or {}).get("ignore_videoresize", False)
    )

    while True:
        event = pygame.event.wait()
        _debug_menu(
            f"evento {pygame.event.event_name(event.type) if hasattr(pygame.event, 'event_name') else event.type} ({getattr(event, 'w', '')}x{getattr(event, 'h', '')})"
        )
        if event.type == pygame.QUIT:
            _debug_menu("show_main_menu FIN -> salir")
            return "salir"
        if event.type == pygame.VIDEORESIZE:
            if ignore_videoresize:
                _debug_report_videoresize_stats()
                continue
            _debug_count_videoresize()
            now_ms = time.time() * 1000
            if now_ms - get_last_set_mode_time_ms() < VIDEORESIZE_COOLDOWN_MS:
                _debug_report_videoresize_stats()
                continue
            new_w = max(MIN_WINDOW_WIDTH, event.w)
            new_h = max(MIN_WINDOW_HEIGHT, event.h)
            cur_w, cur_h = screen.get_size()
            if abs(new_w - cur_w) > VIDEORESIZE_TOLERANCE_PX or abs(new_h - cur_h) > VIDEORESIZE_TOLERANCE_PX:
                screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                track_set_mode()
                _debug_count_set_mode()
                _draw_main_menu(screen, options, selected)
            _debug_report_videoresize_stats()
        elif event.type == pygame.KEYDOWN:
            if not getattr(event, "repeat", False):
                new_selected, action = _handle_main_menu_key(
                    event, selected, len(options)
                )
                selected = new_selected
                if action:
                    _debug_menu(f"show_main_menu FIN -> {action}")
                    return action
            _draw_main_menu(screen, options, selected)


def _open_config_secondary_window(profile_data):
    screen, primary_size = open_secondary_window(
        "Configuracion de perfiles", size=(460, 320), window_mode=_current_window_mode
    )
    updated = open_profile_config_menu(screen, profile_data)
    restored = restore_primary_window(
        primary_size, window_mode=_current_window_mode, title="Arcade HUD Overlay"
    )
    return updated, restored


def _run_hud_setup_interactive(profile, profile_data):
    button_count, screen = _run_secondary_selector(
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
            "Modo de entrada",
            SELECTOR_WINDOW_SIZE,
            lambda s: choose_input_mode(s, profile["input_mode"]),
        )
        if mode_choice is None:
            return None
        if mode_choice in ["teclado", "hitbox", "mixbox"]:
            keyboard_action, screen = _confirm_keyboard_remap_secondary()
            if keyboard_action == "cancelar":
                continue
            select_status, screen = _choose_keyboard_device_secondary(
                profile.get("preferred_keyboard_path")
            )
            if select_status[0] == "cancelar":
                continue
            profile["preferred_keyboard_path"] = select_status[1]
            wants_keyboard_remap = keyboard_action == "si"
            input_mode = mode_choice
            break
        diagnostic, screen = _run_secondary_selector(
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


def _run_keyboard_mapping_flow(screen, profile, button_count, interactive_setup):
    if profile["key_bindings"] and any(
        k not in profile["key_bindings"]
        for k in ["Arriba", "Abajo", "Izquierda", "Derecha"]
        + get_button_labels(button_count)
    ):
        profile["key_bindings"] = {}
    if not profile["key_bindings"]:
        if not interactive_setup:
            print("[WARN] Perfil sin key_bindings en modo no interactivo.")
            return False, screen
        mapped, new_screen = _run_secondary_selector(
            "Mapeo teclado", MAPPER_WINDOW_SIZE, lambda s: map_keys(s, button_count)
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
    if not profile["joystick_bindings"]:
        mapped, new_screen = _run_secondary_selector(
            "Mapeo joystick",
            MAPPER_WINDOW_SIZE,
            lambda s: map_joystick_buttons(
                s,
                button_count,
                show_error=False,
                device_path=selected_device_path,
                controller_style=profile.get("controller_style", "default"),
            ),
        )
        if not mapped:
            return False, screen
        profile["joystick_bindings"] = mapped
        profile["joystick_bindings_style"] = profile.get("controller_style", "default")
        screen = new_screen
    return True, screen


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
    load_icons(button_count, profile["button_icons"], enable_icons=not tournament_mode)
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
    threading.Thread(
        target=start_input_listener,
        args=(
            input_mode,
            button_count,
            input_state,
            selected_device_path,
            profile.get("preferred_keyboard_path"),
        ),
        daemon=True,
    ).start()
    clock = pygame.time.Clock()
    running = True
    bg = get_background_color(profile_data.get("capture_mode", "normal"))
    target_fps = TOURNAMENT_FPS if tournament_mode else FPS
    training_state = create_training_state()
    ignore_videoresize = (
        os.environ.get("HUD_IGNORE_VIDEORESIZE") == "1"
        or profile_data.get("ignore_videoresize", False)
    )
    while running:
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        pending_resize = None
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                _debug_count_videoresize()
                pending_resize = (event.w, event.h)
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif (
                    not getattr(event, "repeat", False)
                    and event.key == pygame.K_EQUALS
                    and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
                ):
                    _launch_easteregg_instance()
                elif event.key == pygame.K_TAB:
                    if training_state["status"] == "recording":
                        stop_recording(training_state)
                    else:
                        start_recording(training_state)
                elif event.key == pygame.K_RETURN:
                    if keys[pygame.K_BACKSPACE]:
                        if has_sequence(training_state):
                            _launch_training_window(sequence_to_dict(training_state))
                    else:
                        if training_state["status"] == "recording":
                            stop_recording(training_state)
                        if has_sequence(training_state):
                            start_playback(training_state)
                elif event.key == pygame.K_BACKSPACE and not keys[pygame.K_RETURN]:
                    clear_sequence(training_state)
        snapshot_if_recording(training_state, input_state)
        if training_state["status"] == "playing":
            update_playback(training_state, input_state)
        screen.fill(bg)
        draw_hud(screen, input_state, button_count)
        pygame.display.flip()
        if pending_resize is not None and not ignore_videoresize:
            now_ms = time.time() * 1000
            if now_ms - get_last_set_mode_time_ms() >= VIDEORESIZE_COOLDOWN_MS:
                new_w = max(MIN_WINDOW_WIDTH, pending_resize[0])
                new_h = max(MIN_WINDOW_HEIGHT, pending_resize[1])
                cur_w, cur_h = screen.get_size()
                if abs(new_w - cur_w) > VIDEORESIZE_TOLERANCE_PX or abs(new_h - cur_h) > VIDEORESIZE_TOLERANCE_PX:
                    screen = pygame.display.set_mode(
                        (new_w, new_h),
                        pygame.RESIZABLE,
                    )
                    track_set_mode()
                    _debug_count_set_mode()
        _debug_report_videoresize_stats()
        time.sleep(0.005)
        clock.tick(target_fps)


def run_hud_session(
    screen, profile_data, interactive_setup=True, force_tournament=False
):
    profile = get_active_profile(profile_data)
    if interactive_setup:
        result = _run_hud_setup_interactive(profile, profile_data)
        if result is None:
            return False
        (
            button_count,
            input_mode,
            selected_device_path,
            wants_keyboard_remap,
            setup_screen,
        ) = result
        if setup_screen is not None:
            screen = setup_screen
    else:
        button_count, input_mode, selected_device_path, wants_keyboard_remap, _ = (
            _run_hud_setup_non_interactive(profile)
        )

    profile["button_count"] = button_count
    profile["input_mode"] = input_mode
    profile["preferred_joystick_path"] = selected_device_path
    labels = get_button_labels(button_count)
    profile["button_icons"] = {lbl: profile["button_icons"].get(lbl) for lbl in labels}
    if profile["joystick_bindings"] and any(
        lbl not in profile["joystick_bindings"] for lbl in labels
    ):
        profile["joystick_bindings"] = {}
    if input_mode in ["teclado", "hitbox", "mixbox"] and wants_keyboard_remap:
        profile["key_bindings"] = {}

    if input_mode in ["teclado", "hitbox", "mixbox"]:
        ok, screen = _run_keyboard_mapping_flow(
            screen, profile, button_count, interactive_setup
        )
        if not ok:
            return False
    if input_mode == "joystick":
        ok, screen = _run_joystick_mapping_flow(
            screen, profile, button_count, selected_device_path
        )
        if not ok:
            return False

    sync_active_profile_to_legacy_files(profile_data)
    save_profiles_data(profile_data)
    input_state = {"stick": [0, 0], "buttons": [False] * len(labels)}
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
    global _current_window_mode
    pygame.init()
    os.environ["SDL_VIDEO_WINDOW_POS"] = "100,100"
    _current_window_mode = "floating_hint"
    screen = _set_window_size(MENU_WIDTH, MENU_HEIGHT, "Arcade HUD Overlay")

    profile_data = load_profiles_data()
    _current_window_mode = (
        "normal"
        if os.environ.get("HUD_WINDOW_MODE_NORMAL") == "1"
        else profile_data.get("window_mode", "floating_hint")
    )
    set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
    while True:
        _current_window_mode = (
            "normal"
            if os.environ.get("HUD_WINDOW_MODE_NORMAL") == "1"
            else profile_data.get("window_mode", "floating_hint")
        )
        set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
        action = show_main_menu(screen, profile_data)
        _debug_menu(f"main loop action={action}")
        if action == "salir":
            confirmed, screen = _confirm_exit_secondary()
            if confirmed:
                break
            _debug_menu("main loop continue (salir cancelado)")
            continue
        if action == "configurar":
            updated, screen = _open_config_secondary_window(profile_data)
            if updated:
                profile_data = updated
                save_profiles_data(profile_data)
                set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
            _debug_menu("main loop continue (configurar)")
            continue
        if action == "iniciar":
            screen = _set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT, "Arcade HUD Overlay")
            run_hud_session(screen, profile_data)
            screen = _set_window_size(MENU_WIDTH, MENU_HEIGHT, "Arcade HUD Overlay")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
