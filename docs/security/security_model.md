# Modelo de confianza y seguridad (Joystick Overlay, Linux)

Este documento resume **qué se considera confiable**, **qué no**, y **qué hace el código** para limitar daños por archivos hostiles. No sustituye una auditoría formal ni promete seguridad absoluta.

## Raíces de datos

| Área | Ruta típica (canon) | Mutable |
|------|---------------------|--------|
| Datos de usuario | `user/` bajo la raíz del proyecto | Sí |
| Perfiles | `user/profiles/<id>/` (`profile.json`, JSON de bindings, `icons/`) | Sí |
| Índice de perfiles | `user/profiles_index.json` | Sí |
| Assets empaquetados | `arcade/assets/` (icon packs, plantillas, `.assets_version`) | Semimutable (actualización / release) |

Los **ZIP de perfil** (importar/exportar desde la app) y los **ZIP de actualización** (`scripts/update.sh --zip`) se tratan como **entrada no confiable**: pueden intentar path traversal, ZIP slip, symlinks o bombas de compresión.

## Políticas implementadas (resumen)

### Importación de perfil (Python)

- Extracción con [`utils/safe_zip_extract.py`](../../arcade/engine/utils/safe_zip_extract.py): sin `extractall` ciego; comprobación de ruta bajo el directorio temporal; rechazo de symlinks y nodos especiales (modo Unix en `ZipInfo`); límites de número de miembros y tamaño descomprimido.
- Iconos importados solo como **ficheros regulares** con extensión permitida; destino bajo `user/profiles/<id>/icons/`, no bajo el directorio de trabajo actual.
- Bindings copiados solo con nombres canónicos y **sin** seguir enlaces al leer desde el temporal.

### Resolución de rutas (HUD / iconos)

- Rutas relativas de iconos y fondo deben quedar **bajo el directorio del perfil** (resolución canónica y contención).
- Rutas absolutas de override solo si quedan bajo `user/` o bajo `arcade/assets/`.
- No se resuelven iconos contra el **cwd** del proceso.
- Nombre de **icon pack**: solo packs que existan en disco bajo `arcade/assets/icon_packs/<pack>/buttons/`.

### Actualización por ZIP (`update.sh`)

- Bloqueo exclusivo `flock` en `user/update.lock` durante el flujo `--zip` para evitar dos actualizaciones a la vez.
- Tras `unzip`, barrido con `find`: falla si hay **symlinks** o entradas que no sean fichero o directorio regular.
- Copia con `cp -rL` (sigue enlaces al leer el origen; no preserva symlinks como tal en el destino del proyecto).

### Guardado de perfiles

- Escritura del índice y ficheros de perfil bajo **mutex** `fcntl` (`user/profiles_index.lock`) para reducir corrupción por procesos concurrentes (no sustituye un único proceso escritor en todos los escenarios).

## Qué no está en alcance

- **Firma criptográfica** de releases ni canal tipo TUF/Sigstore.
- Confiar ciegamente en ZIPs de terceros sigue siendo riesgo de **supply chain**; se recomienda obtener builds desde **fuente oficial** y verificar fuera de banda cuando sea posible.

## Verificación local

Tras cambios de seguridad, conviene ejecutar en tu entorno (con venv si aplica):

- `PYTHONPATH=arcade/engine python3 tests/test_zip_security.py`
- `PYTHONPATH=arcade/engine python3 tests/test_bindings_format_slab.py`
