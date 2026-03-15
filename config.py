# config.py

# Ventana
SCREEN_WIDTH = 375
SCREEN_HEIGHT = 175
FPS = 60
MAX_JOYSTICK_RETRIES = 3

# Joystick
JOYSTICK_CENTER = (75, 85)
JOYSTICK_RADIUS = 50
JOYSTICK_STICK_LENGTH = 40

# Botón (radio constante)
BUTTON_RADIUS = 30

# Ruta para guardar bindings si se usa teclado
BINDINGS_PATH = "bindings.json"
JOYSTICK_BINDINGS_PATH = "joystick_bindings.json"
PROFILES_PATH = "profiles.json"

# Filtro de nombre de dispositivo joystick
DEVICE_NAME_FILTER = ["joystick", "gamepad"]
SUPPORTED_BUTTON_COUNTS = [4, 6, 8]
SUPPORTED_CONTROLLER_STYLES = ["default", "playstation", "xbox", "switch"]
SUPPORTED_CAPTURE_MODES = ["normal", "obs_green"]

# Easteregg: al presionar Space sobre "Iniciar HUD" se abre otra instancia.
EASTEREGG_ENABLE_MULTI_INSTANCE = True
EASTEREGG_MULTI_INSTANCE_KEY = "space"
EASTEREGG_MAX_INSTANCES = 3

# Colores
COLOR_BG = (0, 0, 0, 0)  # Verde brillante para OBS Studio,  utiliza (0, 255, 0)
# COLOR_BG = (0, 255, 0)
COLOR_STICK = (100, 100, 100)
COLOR_STICK_KNOB = (0, 255, 0)
COLOR_BUTTON_INACTIVE = (80, 80, 80)
COLOR_BUTTON_ACTIVE = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)
JOYSTICK_COLOR_PRESETS = {
    "verde": [0, 255, 0],
    "azul": [80, 160, 255],
    "rojo": [255, 70, 70],
    "morado": [180, 80, 255],
    "blanco": [240, 240, 240],
}

# -------------------------------
# FUNCIONES DE CONFIGURACIÓN DINÁMICA
# -------------------------------


def get_button_labels(button_count):
    if button_count == 4:
        return ["LP", "LK", "HP", "HK"]
    if button_count == 8:
        return ["LP", "MP", "HP", "TR", "LK", "MK", "HK", "BR"]
    return ["LP", "MP", "HP", "LK", "MK", "HK"]


def get_bindings_format_key(button_count):
    if button_count == 4:
        return "formato_4"
    if button_count == 8:
        return "formato_8"
    return "formato_6"


def get_icon_paths(button_count):
    return [get_default_icon_path(label) for label in get_button_labels(button_count)]


def get_default_icon_path(label):
    return f"icons/{label.lower()}.png"


def get_button_positions(button_count):
    if button_count == 8:
        full_positions = {
            "LP": (165, 50),
            "MP": (225, 50),
            "HP": (285, 50),
            "TR": (345, 50),
            "LK": (165, 130),
            "MK": (225, 130),
            "HK": (285, 130),
            "BR": (345, 130),
        }
    else:
        full_positions = {
            "LP": (195, 50),
            "MP": (265, 50),
            "HP": (335, 50),
            "LK": (195, 130),
            "MK": (265, 130),
            "HK": (335, 130),
        }
    return [full_positions[label] for label in get_button_labels(button_count)]


def get_controller_button_name(label, controller_style):
    controller_maps = {
        "playstation": {
            "LP": "Cuadrado",
            "MP": "Triangulo",
            "HP": "R1",
            "TR": "R2",
            "LK": "X",
            "MK": "Circulo",
            "HK": "L1",
            "BR": "L2",
        },
        "xbox": {
            "LP": "X",
            "MP": "Y",
            "HP": "RB",
            "TR": "RT",
            "LK": "A",
            "MK": "B",
            "HK": "LB",
            "BR": "LT",
        },
        "switch": {
            "LP": "Y",
            "MP": "X",
            "HP": "R",
            "TR": "ZR",
            "LK": "B",
            "MK": "A",
            "HK": "L",
            "BR": "ZL",
        },
    }

    if controller_style in controller_maps:
        return controller_maps[controller_style].get(label, label)
    return label


def get_hud_fallback_text(label, controller_style):
    short_maps = {
        "playstation": {
            "Cuadrado": "SQ",
            "Triangulo": "TRI",
            "Circulo": "O",
            "X": "X",
        },
        "xbox": {
            "A": "A",
            "B": "B",
            "X": "X",
            "Y": "Y",
        },
        "switch": {
            "A": "A",
            "B": "B",
            "X": "X",
            "Y": "Y",
        },
    }
    controller_name = get_controller_button_name(label, controller_style)
    if controller_style in short_maps:
        return short_maps[controller_style].get(controller_name, controller_name)
    return label


def get_background_color(capture_mode):
	if capture_mode == "obs_green":
		return (0, 255, 0)
	return (0, 0, 0)
