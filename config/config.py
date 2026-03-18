# config/config.py - Configuración del proyecto

# Ventana
SCREEN_WIDTH = 375
SCREEN_HEIGHT = 175
MIN_WINDOW_WIDTH = 200
MIN_WINDOW_HEIGHT = 120
VIDEORESIZE_COOLDOWN_MS = 150
VIDEORESIZE_TOLERANCE_PX = 5
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 48
FPS = 60
TOURNAMENT_FPS = 30
MAX_JOYSTICK_RETRIES = 3

# Joystick
JOYSTICK_CENTER = (75, 85)
JOYSTICK_RADIUS = 50
JOYSTICK_STICK_LENGTH = 40

# Botón (radio constante)
BUTTON_RADIUS = 30

# Hitbox/Mixbox: márgenes para evitar solapamiento direccionales-botones
HITBOX_MIXBOX_DIRECTION_LEFT = 40
HITBOX_MIXBOX_BUTTONS_LEFT = 130
HITBOX_MIXBOX_GAP_BETWEEN_ZONES = 35
HITBOX_DIRECTION_DIAGONAL_STEP = 25

# Ruta para guardar bindings si se usa teclado
BINDINGS_PATH = "json/bindings.json"
JOYSTICK_BINDINGS_PATH = "json/joystick_bindings.json"
PROFILES_PATH = "json/profiles.json"
FONTS_DIR = "fonts"

# Filtro de nombre de dispositivo joystick
DEVICE_NAME_FILTER = ["joystick", "gamepad"]
SUPPORTED_BUTTON_COUNTS = [4, 6, 8]
SUPPORTED_CONTROLLER_STYLES = ["default", "playstation", "xbox", "switch"]
SUPPORTED_CAPTURE_MODES = ["normal", "obs_green"]
SUPPORTED_INPUT_MODES = ["teclado", "joystick", "hitbox", "mixbox"]
SUPPORTED_MONO_FONT_FAMILIES = ["JetBrainsMono", "FiraCode", "Hack"]
DEFAULT_MONO_FONT_FAMILY = "JetBrainsMono"

MONO_FONT_CONFIG = {
    "JetBrainsMono": {
        "regular_path": f"{FONTS_DIR}/JetBrainsMonoNerdFont-Regular.ttf",
        "bold_path": f"{FONTS_DIR}/JetBrainsMonoNerdFont-Bold.ttf",
        "system_name": "JetBrainsMono Nerd Font",
    },
    "FiraCode": {
        "regular_path": f"{FONTS_DIR}/FiraCodeNerdFont-Regular.ttf",
        "bold_path": f"{FONTS_DIR}/FiraCodeNerdFont-Bold.ttf",
        "system_name": "FiraCode Nerd Font",
    },
    "Hack": {
        "regular_path": f"{FONTS_DIR}/HackNerdFont-Regular.ttf",
        "bold_path": f"{FONTS_DIR}/HackNerdFont-Bold.ttf",
        "system_name": "Hack Nerd Font",
    },
}

# Easteregg: al presionar = sobre "Iniciar HUD" se abre otra instancia.
EASTEREGG_ENABLE_MULTI_INSTANCE = True
EASTEREGG_MULTI_INSTANCE_KEY = "equals"
EASTEREGG_MAX_INSTANCES = 3

# Colores
COLOR_BG = (0, 0, 0, 0)
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
DEFAULT_HEX_COLOR = "#00FF00"

BUTTON_COLOR_PRESETS = {
    "gris_rojo": {"inactive": [80, 80, 80], "active": [255, 0, 0]},
    "gris_verde": {"inactive": [80, 80, 80], "active": [0, 255, 0]},
    "gris_azul": {"inactive": [80, 80, 80], "active": [80, 160, 255]},
    "oscuro_amarillo": {"inactive": [50, 50, 50], "active": [255, 220, 0]},
    "oscuro_blanco": {"inactive": [60, 60, 60], "active": [240, 240, 240]},
}


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


def get_hud_scale(screen_width, screen_height):
    scale_x = screen_width / SCREEN_WIDTH
    scale_y = screen_height / SCREEN_HEIGHT
    scale = min(scale_x, scale_y)
    return max(0.5, min(2.0, scale))


def get_button_positions(button_count, screen_width=None, screen_height=None):
    base = _get_button_positions_base(button_count)
    if screen_width is None or screen_height is None:
        return base
    scale = get_hud_scale(screen_width, screen_height)
    return [(int(x * scale), int(y * scale)) for x, y in base]


def _get_button_positions_base(button_count):
    if button_count == 4:
        return [
            (220, 50),  # LP - columna izq, arriba
            (220, 130),  # LK - columna izq, abajo
            (285, 50),  # HP - columna der, arriba
            (285, 130),  # HK - columna der, abajo
        ]
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


def _get_button_positions_hitbox_mixbox_base(button_count):
    """Layout Hitbox/Mixbox: direccionales a la izquierda, botones de impacto desplazados a la derecha (HITBOX_MIXBOX_BUTTONS_LEFT)."""
    dx = HITBOX_MIXBOX_BUTTONS_LEFT - 95
    dx_8 = 0
    if button_count == 4:
        return {
            "LP": (210 + dx, 140),
            "LK": (260 + dx, 75),
            "HP": (330 + dx, 50),
            "HK": (400 + dx, 55),
        }
    if button_count == 8:
        return {
            "LP": (95 + dx_8, 90),
            "MP": (165 + dx_8, 50),
            "HP": (235 + dx_8, 50),
            "TR": (345 + dx_8, 50),
            "LK": (95 + dx_8, 130),
            "MK": (165 + dx_8, 90),
            "HK": (235 + dx_8, 90),
            "BR": (345 + dx_8, 90),
        }
    # 6 botones
    return {
        "LP": (95 + dx, 90),
        "MP": (195 + dx, 50),
        "HP": (295 + dx, 50),
        "LK": (95 + dx, 130),
        "MK": (195 + dx, 90),
        "HK": (295 + dx, 90),
    }


def get_button_positions_hitbox_mixbox(button_count, screen_width, screen_height):
    base = _get_button_positions_hitbox_mixbox_base(button_count)
    labels = get_button_labels(button_count)
    positions = [base[label] for label in labels]
    if screen_width is None or screen_height is None:
        return positions
    scale = get_hud_scale(screen_width, screen_height)
    return [(int(x * scale), int(y * scale)) for x, y in positions]


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


PLAYSTATION_SYMBOLS = {
    "LP": "\u25a0",
    "MP": "\u25b2",
    "LK": "\u2715",
    "MK": "\u25cf",
    "HP": "R1",
    "TR": "R2",
    "HK": "L1",
    "BR": "L2",
}

XBOX_4_BUTTONS = {"LP": "A", "LK": "B", "HP": "Y", "HK": "X"}
SWITCH_4_BUTTONS = {"LP": "B", "LK": "A", "HP": "X", "HK": "Y"}
PLAYSTATION_4_BUTTONS = {"LP": "\u25a0", "LK": "\u2715", "HP": "\u25b2", "HK": "\u25cf"}


def get_hud_fallback_text(label, controller_style, button_count=None):
    if button_count == 4:
        if controller_style == "playstation":
            return PLAYSTATION_4_BUTTONS.get(label, label)
        if controller_style == "xbox":
            return XBOX_4_BUTTONS.get(label, label)
        if controller_style == "switch":
            return SWITCH_4_BUTTONS.get(label, label)
    short_maps = {
        "xbox": {"A": "A", "B": "B", "X": "X", "Y": "Y"},
        "switch": {"A": "A", "B": "B", "X": "X", "Y": "Y"},
    }
    if controller_style == "playstation":
        return PLAYSTATION_SYMBOLS.get(label, label)
    controller_name = get_controller_button_name(label, controller_style)
    if controller_style in short_maps:
        return short_maps[controller_style].get(controller_name, controller_name)
    return label


def get_background_color(capture_mode):
    if capture_mode == "obs_green":
        return (0, 255, 0)
    return (0, 0, 0)


def normalize_mono_font_family(font_family):
    if font_family in SUPPORTED_MONO_FONT_FAMILIES:
        return font_family
    return DEFAULT_MONO_FONT_FAMILY


def get_mono_font_config(font_family):
    return MONO_FONT_CONFIG[normalize_mono_font_family(font_family)]


def parse_hex_color(color_text):
    if not isinstance(color_text, str):
        return None
    value = color_text.strip()
    if value.startswith("#"):
        value = value[1:]
    if len(value) != 6:
        return None
    try:
        return [int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)]
    except Exception:
        return None


def rgb_to_hex(color_values):
    if not isinstance(color_values, list) or len(color_values) != 3:
        return DEFAULT_HEX_COLOR
    return "#{:02X}{:02X}{:02X}".format(
        max(0, min(255, int(color_values[0]))),
        max(0, min(255, int(color_values[1]))),
        max(0, min(255, int(color_values[2]))),
    )
