# main.py

# ---Archivo principal ---

import engine_sys_path  # noqa: F401, E402 — debe ir antes de imports locales arcade/engine

import os
os.environ.setdefault("SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR", "0")

import pygame
import sys
import time
import warnings

from app.hud_session import run_hud_session
from app.main_menu import (
    AppContext,
    MainMenuState,
    drive_menu_frame as _drive_menu_frame,
    run_main_menu_until_action,
)
from app.debug_menu import debug_menu as _debug_menu
from app.secondary_flows import (
    confirm_exit_secondary as _confirm_exit_secondary,
    select_profile_secondary,
    set_window_size as _set_window_size,
)
from app.startup import (
    do_reset_data as _do_reset_data,
    preflight_startup as _preflight_startup,
    run_reset_data_confirmation as _run_reset_data_confirmation,
)
from app.window_mode import set_window_mode

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WINDOW_CAPTION_APP,
    DATA_VERSION_PATH,
    ASSETS_VERSION_PATH,
    RUNTIME_VERSION_PATH,
    USER_DIR,
    PROFILES_DIR,
    RESET_LOG_PATH,
    USER_BACKUPS_DIR,
    BACKUP_PROFILES_ROOT,
    ensure_contract_dirs,
    get_data_version,
    get_assets_version,
    get_runtime_version,
    write_data_version,
)
from render import open_profile_config_menu
from render.backup_welcome import run_backup_welcome_if_needed
from render.first_run_wizard import run_first_run_wizard_if_needed
from profiles import load_profiles_data, save_profiles_data
from utils import set_ui_font_family
from core.state_manager import StateManager


def _open_config_secondary_window(screen, profile_data):
    updated = open_profile_config_menu(screen, profile_data)
    return updated, screen


def show_main_menu(screen, profile_data=None):
    warnings.warn(
        "show_main_menu está deprecado; usa run_main_menu_until_action",
        DeprecationWarning,
        stacklevel=2,
    )
    return run_main_menu_until_action(screen, profile_data)


def main():
    if "--do-reset-data" in sys.argv[1:]:
        return _do_reset_data()
    if "--reset-data" in sys.argv[1:]:
        return _run_reset_data_confirmation()
    if not _preflight_startup():
        return
    pygame.init()
    os.environ["SDL_VIDEO_WINDOW_POS"] = "100,100"
    set_window_mode("floating_hint")
    # Una sola superficie al tamaño del HUD: evita set_mode menú↔HUD y mantiene foco/captura (p. ej. OBS).
    screen = _set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_CAPTION_APP)

    profile_data = load_profiles_data()
    profile_data = run_backup_welcome_if_needed(screen, profile_data)
    profile_data = run_first_run_wizard_if_needed(screen, profile_data)
    set_window_mode(
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
        set_window_mode(
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

        screen = _drive_menu_frame(screen, ctx, sm, clock)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
