# config.py

# Ventana
SCREEN_WIDTH = 375
SCREEN_HEIGHT = 175
FPS = 60

# Joystick
JOYSTICK_CENTER = (75, 85)
JOYSTICK_RADIUS = 50
JOYSTICK_STICK_LENGTH = 40

# Botón (radio constante)
BUTTON_RADIUS = 30

# Ruta para guardar bindings si se usa teclado
BINDINGS_PATH = "bindings.json"

# Filtro de nombre de dispositivo joystick
DEVICE_NAME_FILTER = ["joystick", "gamepad"]

# Colores
COLOR_BG = (0, 0, 0, 0) # Verde brillante para OBS Studio,  utiliza (0, 255, 0)
COLOR_STICK = (100, 100, 100)
COLOR_STICK_KNOB = (0, 255, 0)
COLOR_BUTTON_INACTIVE = (80, 80, 80)
COLOR_BUTTON_ACTIVE = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)

# -------------------------------
# FUNCIONES DE CONFIGURACIÓN DINÁMICA
# -------------------------------

def get_button_labels(button_count):
    if button_count == 4:
        return ["LP", "LK", "HP", "HK"]
    else: # Por defecto o si es 6
        return ["LP", "MP", "HP", "LK", "MK", "HK"]

def get_icon_paths(button_count):
    icon_map = {
        "LP": "icons/lp.png", "MP": "icons/mp.png", "HP": "icons/hp.png",
        "LK": "icons/lk.png", "MK": "icons/mk.png", "HK": "icons/hk.png",
    }
    return [icon_map[label] for label in get_button_labels(button_count)]

def get_button_positions(button_count):
    full_positions = {
        "LP": (195, 50), "MP": (265, 50), "HP": (335, 50),
        "LK": (195, 130), "MK": (265, 130), "HK": (335, 130),
    }
    return [full_positions[label] for label in get_button_labels(button_count)]
