# Métricas y pruebas de calidad - HUD Overlay

Estructura de pruebas y métricas de calidad del proyecto. Los scripts pueden ejecutarse localmente o en CI (con `SDL_VIDEODRIVER=dummy` para tests gráficos sin display).

## Dependencias de desarrollo

```bash
pip install -r test/requirements-dev.txt
```

O en un entorno virtual:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt -r test/requirements-dev.txt
```

## Estructura

```
hud_overlay/
  config/         # Configuración
  utils/          # Utilidades (utils, image_file_picker)
  profiles/       # Persistencia de perfiles
  render/         # UI (hud_renderer, profile_config_menu, selectores)
  maps/           # Mapeo (keymapper, joystick_mapper, input_reader)
  main.py, configure.py, tournament.py  # Puntos de entrada

test/
  run_cyclomatic.py      # Complejidad ciclomática (radon)
  run_dit.py             # Profundidad de herencia (DIT)
  run_cbo.py             # Acoplamiento entre módulos (imports)
  test_fps.py            # FPS en sesión HUD
  test_resource_usage.py # CPU y memoria
  test_menu_minimal.py   # Menú mínimo (depurar parpadeo)
  requirements-dev.txt   # radon, psutil, pytest
```

## Scripts de métricas

### Complejidad ciclomática (run_cyclomatic.py)

Falla si alguna función supera el umbral (por defecto 10).

```bash
python test/run_cyclomatic.py
python test/run_cyclomatic.py --threshold 12
```

**Baseline:** Umbral CC=10. El script falla si alguna función supera 10. El código actual puede tener violaciones; el umbral sirve como meta de calidad para refactorización gradual.

### Profundidad de herencia (run_dit.py)

Reporta DIT de las clases. El proyecto es mayormente procedural/funcional.

```bash
python test/run_dit.py
```

**Baseline:** Proyecto con bajo uso de herencia; DIT típicamente 1.

### Acoplamiento (run_cbo.py)

Cuenta imports por módulo. Falla si algún módulo supera el umbral (por defecto 15).

```bash
python test/run_cbo.py
python test/run_cbo.py --threshold 20
```

**Baseline:** Umbral 15 imports por módulo.

### FPS (test_fps.py)

Mide FPS durante una sesión HUD de 3 segundos. Requiere display o `SDL_VIDEODRIVER=dummy`.

```bash
SDL_VIDEODRIVER=dummy python test/test_fps.py
```

**Baseline:** FPS ≥ 75% del objetivo (60 normal, 30 tournament). Mínimo aceptable ~45 FPS para modo normal.

### Uso de recursos (test_resource_usage.py)

Mide CPU y memoria durante 5 segundos de ejecución HUD.

```bash
SDL_VIDEODRIVER=dummy python test/test_resource_usage.py
```

**Baseline:** Memoria < 200 MB, CPU < 95%. Valores dependen del entorno (CI vs local).

### Menú mínimo (test_menu_minimal.py)

Muestra solo el menú principal, sin config ni HUD. Útil para depurar parpadeo o reproducir el menú de forma aislada.

```bash
python test/test_menu_minimal.py
```

Requiere display o `SDL_VIDEODRIVER=dummy`.

## Ejecución en CI

Para entornos sin display (GitHub Actions, etc.):

```bash
export SDL_VIDEODRIVER=dummy
python test/run_cyclomatic.py
python test/run_dit.py
python test/run_cbo.py
python test/test_fps.py
python test/test_resource_usage.py
```

Los tests de FPS y recursos pueden marcarse como opcionales si el entorno no tiene suficiente capacidad para reproducir resultados estables.

## Aviso AVX2 (pygame)

Al ejecutar el proyecto puede aparecer:

```
RuntimeWarning: Your system is avx2 capable but pygame was not built with support for it.
```

Es un aviso inofensivo: pygame se instaló sin detección AVX2 en tiempo de compilación. No afecta al funcionamiento. Para eliminarlo habría que recompilar pygame con `PYGAME_DETECT_AVX2=1` antes de compilar.
