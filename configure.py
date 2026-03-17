import os
import sys
import pygame

import main as main_app
from profiles import load_profiles_data, save_profiles_data
from render import open_profile_config_menu
from utils import set_ui_font_family

def main():
	pygame.init()
	os.environ["SDL_VIDEO_WINDOW_POS"] = "100,100"

	profile_data = load_profiles_data()
	set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
	main_app._current_window_mode = profile_data.get("window_mode", "floating_hint")
	screen = main_app._set_window_size(460, 320, "Configurar perfiles")
	updated = open_profile_config_menu(screen, profile_data)
	if updated:
		save_profiles_data(updated)

	pygame.quit()
	sys.exit()

if __name__ == "__main__":
	main()
