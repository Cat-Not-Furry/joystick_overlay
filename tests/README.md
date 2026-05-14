# Métricas y pruebas de calidad — Joystick Overlay

Estructura de pruebas y métricas de calidad del proyecto. Los scripts pueden ejecutarse localmente o en CI (con `SDL_VIDEODRIVER=dummy` para tests gráficos sin display).

## Dependencias de desarrollo

```bash
pip install -r tests/requirements-dev.txt
```

O en un entorno virtual:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt -r tests/requirements-dev.txt
```

## Estructura

```
<raíz-del-repo>/
  arcade/engine/  # Código Python (core, config, maps, render, profiles, training, utils)
  arcade/assets/  # Icon packs, fuentes, versionado de assets
  configs/        # Defaults, schema, migraciones (índice + manifiestos)
  main.py, configure.py, tournament.py, cli.py  # Puntos de entrada en raíz

tests/
  run_cyclomatic.py      # Complejidad ciclomática (radon)
  run_dit.py             # Profundidad de herencia (DIT)
  run_cbo.py             # Acoplamiento entre módulos (imports)
  test_fps.py            # FPS en sesión HUD
  test_resource_usage.py # CPU y memoria
  test_menu_minimal.py   # Menú mínimo (depurar parpadeo)
  test_zip_security.py     # Extracción ZIP segura + safe_paths (stdlib)
  requirements-dev.txt   # radon, pytest, psutil (ver fichero en repo)
```

## Scripts de métricas

### Complejidad ciclomática (run_cyclomatic.py)

Falla si alguna función supera el umbral (por defecto 10).

```bash
python tests/run_cyclomatic.py
python tests/run_cyclomatic.py --threshold 12
```

**Baseline:** Umbral CC=10. El script falla si alguna función supera 10. El código actual puede tener violaciones; el umbral sirve como meta de calidad para refactorización gradual.

### Profundidad de herencia (run_dit.py)

Reporta DIT de las clases. El proyecto es mayormente procedural/funcional.

```bash
python tests/run_dit.py
```

**Baseline:** Proyecto con bajo uso de herencia; DIT típicamente 1.

### Acoplamiento (run_cbo.py)

Cuenta imports por módulo. Falla si algún módulo supera el umbral (por defecto **20**). Los entrypoints en la raíz (`main.py`, etc.) suelen importar más módulos que el núcleo bajo `arcade/engine/`; el umbral 20 evita falsos positivos en `main.py` sin relajar el resto del árbol de forma excesiva.

```bash
python tests/run_cbo.py
python tests/run_cbo.py --threshold 15
```

**Baseline:** Umbral **20** imports por módulo (ajustable con `--threshold` para auditorías más estrictas).

**Verificación local rápida** (desde la raíz del repositorio, sin CI obligatoria):

```bash
python tests/run_cbo.py
SDL_VIDEODRIVER=dummy python tests/test_menu_minimal.py
```

### FPS (test_fps.py)

Mide FPS durante una sesión HUD de 3 segundos. Requiere display o `SDL_VIDEODRIVER=dummy`.

```bash
SDL_VIDEODRIVER=dummy python tests/test_fps.py
```

**Baseline:** FPS ≥ 75% del objetivo (60 normal, 30 tournament). Mínimo aceptable ~45 FPS para modo normal.

### Uso de recursos (test_resource_usage.py)

Mide CPU y memoria durante 5 segundos de ejecución HUD.

```bash
SDL_VIDEODRIVER=dummy python tests/test_resource_usage.py
```

**Baseline:** Memoria < 200 MB, CPU < 95%. Valores dependen del entorno (CI vs local).

### Menú mínimo (test_menu_minimal.py)

Muestra solo el menú principal, sin config ni HUD. Útil para depurar parpadeo o reproducir el menú de forma aislada. El script añade la **raíz del repositorio** y **`arcade/engine`** a `sys.path` para poder `import main` y los paquetes del motor.

```bash
# Desde la raíz del clon:
SDL_VIDEODRIVER=dummy python tests/test_menu_minimal.py
# o con sesión gráfica:
python tests/test_menu_minimal.py
```

Requiere display o `SDL_VIDEODRIVER=dummy`.

## Ejecución en CI

Para entornos sin display (GitHub Actions, etc.):

```bash
export SDL_VIDEODRIVER=dummy
python tests/run_cyclomatic.py
python tests/run_dit.py
python tests/run_cbo.py
python tests/test_fps.py
python tests/test_resource_usage.py
```

Los tests de FPS y recursos pueden marcarse como opcionales si el entorno no tiene suficiente capacidad para reproducir resultados estables.

## Aviso AVX2 (pygame)

Al ejecutar el proyecto puede aparecer:

```
RuntimeWarning: Your system is avx2 capable but pygame was not built with support for it.
```

Es un aviso inofensivo: pygame se instaló sin detección AVX2 en tiempo de compilación. No afecta al funcionamiento. Para eliminarlo habría que recompilar pygame con `PYGAME_DETECT_AVX2=1` antes de compilar.
