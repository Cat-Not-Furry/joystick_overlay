import os
import sys
import pygame

import engine_sys_path  # noqa: F401, E402

import main as main_app
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_CAPTION_APP
from profiles import load_profiles_data, save_profiles_data, set_active_profile
from render.backup_welcome import run_backup_welcome_if_needed
from utils import set_ui_font_family

def main():
	pygame.init()
	os.environ["SDL_VIDEO_WINDOW_POS"] = "100,100"
	profile_data = load_profiles_data()
	set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
	main_app._current_window_mode = profile_data.get("window_mode", "floating_hint")
	screen = main_app._set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT, f"{WINDOW_CAPTION_APP} — Torneo")
	profile_data = run_backup_welcome_if_needed(screen, profile_data)

	selected_id, screen = main_app.select_profile_secondary(
		profile_data, screen, title="Perfil para torneo"
	)
	if selected_id is None:
		pygame.quit()
		sys.exit()

	set_active_profile(profile_data, selected_id)
	save_profiles_data(profile_data)

	main_app.run_hud_session(screen, profile_data, interactive_setup=False, force_tournament=True)
	pygame.quit()
	sys.exit()

if __name__ == "__main__":
	main()
