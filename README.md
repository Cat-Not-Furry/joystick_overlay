# 🕹️ Arcade HUD Overlay (Linux)

Visualizador gráfico de entradas tipo arcade para joystick o teclado, diseñado como overlay para emuladores.
Perfecto para tutoriales de juegos de pelea, demostraciones de habilidad o como herramienta de entrenamiento.

## Novedades de configuracion y perfiles
- Navegacion de menus con flechas y Enter.
- Las opciones de menu se abren en ventanas secundarias para un flujo mas limpio.
- Las ventanas secundarias fuera de `main.py` funcionan como hijas modales emuladas (bloquean interaccion y restauran foco/tamano/titulo al cerrar).
- Confirmacion de salida en ventana secundaria.
- Texto responsivo en menus (con limites minimos y maximos para mantener legibilidad).
- Soporte de formatos de 4, 6 y 8 botones.
- Sistema de perfiles en `json/profiles.json`.
- Migracion automatica desde `json/bindings.json` y `json/joystick_bindings.json` al iniciar.
- Personalizacion por perfil: color del joystick e icono por boton.
- Cambio de icono con opcion `Seleccionar...` (Linux) y validacion de imagen maxima `512x512`.
- Apartado de fuente mono en configuracion: `JetBrainsMono`, `FiraCode`, `Hack` (por defecto `JetBrainsMono`).
- La UI usa fuente mono regular; solo las etiquetas de botones se renderizan en negrita.
- Colores avanzados por hexa para joystick (`knob`, `barra`, `anillo`).
- Estilo de control por perfil: `default`, `playstation`, `xbox`, `switch`.
- Si un boton no tiene imagen, se dibuja texto segun el estilo del control seleccionado. En PlayStation se usan abreviaciones (SQ, TRI, O, X, R1, L1, etc.).
- Si el estilo de control cambia, el mapeo de joystick se invalida y se solicita remapeo.
- Reintentos de deteccion de joystick con acceso a diagnostico avanzado.
- Modo de captura global: `normal` y `obs_green` (fondo verde croma).
- Modo de entrada `hitbox` con botones circulares: direccionales (L-U-D-R) en curva descendente, botones de acción (LP-LK-HP-HK) en curva ascendente; opción "Posición alternativa" en perfil.
- Modo de entrada `mixbox` con teclas rectangulares (↑←↓→) y layout estilo teclado.
- Exportar/Importar perfiles en ZIP: desde la configuración del perfil puedes exportar a un `.zip` (`profile.json` + carpeta `icons/` con iconos personalizados) o importar desde un ZIP existente (con resolución de conflictos: sobrescribir, renombrar o cancelar).
- `tournament.py`: flujo de torneo (solo elegir perfil y jugar).
- `configure.py`: abrir configuracion grafica sin iniciar HUD.

## Mapeo por estilo de control
- En `Configurar perfiles` puedes elegir `Estilo de control`.
- Al mapear joystick, el mensaje se adapta al estilo:
	- PlayStation: `Presiona boton Triangulo (...)`
	- Xbox: `Presiona boton B (...)`
	- Switch: `Presiona boton X (...)`
- El perfil guarda el estilo usado para mapear joystick.
- Si ya existe mapeo para el estilo actual, se reutiliza.
- Si no existe (o cambias de estilo), el sistema te pide mapear de nuevo.

## Modo OBS / grabacion
- En `Configurar perfiles` ahora existe `Modo de captura`.
- `normal`: fondo negro.
- `obs_green`: fondo verde puro `(0, 255, 0)` para usar con chroma key.
- Este ajuste se guarda en `json/profiles.json` y se aplica cuando inicias el HUD.
- Recomendado en OBS: agrega `Clave de croma` y usa verde como color clave.

## Teclado sin foco (global)
- En `Configurar perfiles` puedes elegir `Teclado global`.
- Si eliges un dispositivo de teclado, el HUD lee entradas con `evdev` aunque la ventana no tenga foco.
- Si el dispositivo no esta disponible o falla, el sistema hace fallback al modo clasico con foco.
- Si pones `ninguno (solo con foco)`, se usa el metodo tradicional de `pygame`.

## Tournament Legal
- El modo torneo se usa desde el entrypoint dedicado.
- Fuerza render minimalista para reducir uso de CPU.
- Evita carga de iconos y usa dibujo plano.
- En torneo el HUD usa `TOURNAMENT_FPS` (por defecto 30) para bajar costo grafico.
- Inicia torneo con:

```bash
python3 tournament.py
```

## Configure standalone
- Para abrir solo la configuracion de perfiles:

```bash
python3 configure.py
```

## Modo entrenamiento
- Durante el HUD: `TAB` inicia grabación (máx. 30 snapshots en 30 s), `ENTER` detiene y reproduce una pasada, `BACKSPACE` borra.
- `ENTER` + `BACKSPACE` (juntas) con secuencia grabada: abre ventana de entrenamiento independiente.
- La ventana hija cierra con `Esc` o al perder foco.

## Easteregg multinstancia
- En el menu principal o durante el HUD, presiona `=` para abrir una nueva instancia.
- Se abre una nueva instancia independiente para comparar dispositivos con amigos.
- Limite de seguridad: maximo `3` instancias simultaneas.

## Anti-parpadeo (overlays y ventana flotante)
- Si el overlay parpadea o el WM no permite hacer la ventana flotante, activa **"Ignorar VIDEORESIZE (anti-parpadeo)"** en Configurar perfiles.
- Con esta opcion activada, el WM puede marcar la ventana como flotante sin conflictos.
- Prueba rapida sin entrar al menu: `HUD_IGNORE_VIDEORESIZE=1 python3 main.py`

## Nota para usuarios con Window Manager (tiling)
- Si usas un WM en mosaico (i3, bspwm, sway, Hyprland, etc.), el gestor puede forzar tamanos grandes o ignorar el tamano inicial solicitado por `pygame`.
- El proyecto intenta fijar tamanos moderados para menu/HUD, pero el WM tiene prioridad final sobre la ventana.
- Si ves que abre muy grande, marca la ventana como flotante desde tu WM para que respete mejor tamano y posicion.
- Si el overlay parpadea, activa "Ignorar VIDEORESIZE (anti-parpadeo)" en Configurar perfiles; asi el WM puede marcar la ventana como flotante sin conflictos.
> [!NOTE]
> Este overlay lo hice para grabar gameplays. Espero te sirva; la lógica no es tan complicada por si quieres personalizarlo. Si lo haces, me haría muy feliz que me mencionaras para ver las mejoras que pudieras haber implementado.

# Estado actual del proyecto 
## (Junio 2025)
### Cosas arregladas
Se redimenciono el tamaño de la ventana del fightstick<br>
Se corrigio el tamaño de las letras y al igual que la interfaz se hubicaron acorde al tamaño de la ventana<br>
Se corrigio el error de main.py (no cargaba key_bindings.json), ya no es necesario remapear en la opcion del teclado, a menos que elimines el archivo, al igual que en el caso de joystick_bindings.json (ambos en `json/`).

## (Agosto 2025)
## Ya que estoy de vacaciones decidi arreglar mi desastre.
### Cosas arregladas
Se arreglo parcialmente la transparecia (necesita filtros como en OBS)<br>
Se mejoro el codigo cada ventana se puede cerrar con el foco o con Esc<br>
Se le dio utilidad al archivo utils.py, para configuraciones que se repiten<br>
**Lo más importante**<br>
Se implemento un entorno virtual para mejor control del sistema y su requirements.txt

## (Marzo 2026)
### Actualización
Se agrego un apartado de fuente monoespaciada en configuracion con 3 opciones: JetBrainsMono, FiraCode y Hack.<br>
La opcion por defecto es JetBrainsMono.<br>
Toda la UI usa variante regular y solo los textos de botones se dibujan en negrita.<br>
Si no existe el archivo local de la fuente, se usa fallback automatico del sistema/pygame para mantener compatibilidad.<br>
En estilo PlayStation sin icono se muestran abreviaciones (SQ, TRI, O, X, R1, L1, etc.).<br>
Opcion `Seleccionar...` en cambio de icono: abre selector nativo Linux (zenity/kdialog/tkinter) y valida imagen maxima 512x512.

### Actualización (layout Hitbox y perfiles ZIP)
- **Layout Hitbox reorganizado**: direccionales (L, U, D, R) en curva descendente de izquierda a derecha; botones de acción (LP, LK, HP, HK) en curva ascendente. Forma general tipo "V" o "U" ergonómica.
- **Exportar/Importar perfiles en ZIP**: desde la configuración del perfil, opciones "Exportar perfil" e "Importar perfil". El ZIP incluye `profile.json` (configuración completa) e `icons/` (solo iconos personalizados). Al importar, si ya existe un perfil con el mismo nombre, se ofrece sobrescribir, renombrar o cancelar.
- **Calidad de código**: análisis de complejidad ciclomática con `python test/run_cyclomatic.py` (umbral CC≤10).

## Bueno, a lo que vinimos...
#### Caracteristicas.

Representación virtual de un fightstick para GNU/Linux.<br>
HUD gráfico en Pygame que se muestra encima de otros programas (overlay).<br>
Visualiza un joystick arcade virtual y hasta 8 botones (configurables).<br>
Modo joystick y modo teclado disponibles.<br>
Permite elegir entre formato de 4, 6 u 8 botones, con layout adaptativo.<br>
Cada botón se representa con íconos (por ejemplo: lp.png, hp.png).<br>
Los íconos se iluminan al presionar los botones reales.

#### Asignación de controles

Al iniciar, pregunta:<br>
¿Formato de botones? (4, 6 o 8)<br>
¿Tipo de entrada? (teclado o joystick)<br>
Si eliges teclado, puedes mapear manualmente teclas por perfil.<br>
Si eliges joystick, puedes mapear cada botón arcade por perfil.<br>
La configuracion principal se guarda en `json/profiles.json`.<br>
Los archivos `json/bindings.json` y `json/joystick_bindings.json` se mantienen para compatibilidad.

#### 📁 Estructura del proyecto

hud_overlay/<br>
├── main.py<br>
├── configure.py<br>
├── tournament.py<br>
├── config/         # Configuracion<br>
├── maps/           # Mapeo (keymapper, joystick_mapper, input_reader)<br>
├── profiles/       # Persistencia de perfiles (profile_store, profile_export)<br>
├── render/         # UI (hud_renderer, profile_config_menu, selectores)<br>
├── training/       # Modo entrenamiento<br>
├── utils/          # Utilidades (file_picker, image_file_picker)<br>
├── test/           # Tests y run_cyclomatic.py<br>
├── json/           # Archivos de usuario (bindings, profiles)<br>
└── icons/<br>
    
Se requiere instalar dependencias con pip.

#### 🐧 Requisitos (Linux)

Python 3.7+
Acceso a /dev/input/*

>[!WARNING]
>Si al ejecutar te da error por no tener permisos para leer dispositivos, utiliza este comando...

```bash
sudo chmod a+r /dev/input/event*
```

>[!NOTE]
>Cuando deje de procrastinar hare una version para Windows y pregare el link <a href="https://github.com/Cat-Not-Furry/hud_overlay/tree/main">aquí</a>
#### ✔️ Características

- Soporta joystick y teclado (vía `evdev`)<br>
- Formatos de 4, 6 u 8 botones<br>
- Asignación personalizada para cada botón<br>
- Compatible con overlays encima de emuladores (como MAME)<br>
- Utiliza entorno virtual para evitar errores.

#### Notas técnicas

Las teclas se guardan en json/bindings.json.<br>
Los botones del joystick se guardan en json/joystick_bindings.json.<br>
Los íconos de los botones se pueden cambiar libremente en icons/.<br>
Puedes expandir el sistema fácilmente para agregar más entradas o estilos visuales.

#### Uso

```bash
git clone https://github.com/Cat-Not-Furry/hud_overlay.git
cd hud_overlay
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Entrypoints disponibles
- `python3 main.py` -> flujo completo (menu principal).
- `python3 tournament.py` -> seleccionar perfil y arrancar en modo torneo.
- `python3 configure.py` -> configurar perfiles sin iniciar HUD.
- `python test/run_cyclomatic.py` -> verificar complejidad ciclomática (CC≤10).

## Si va a utilizar OBS

Cuando selecciones el hud_overlay en OBS:<br>
1. Da click en "Filtros" y en "+", selecciona clave croma o chroma key.<br>
2. En Configurar perfiles, elige **Modo de captura**:
   - **normal**: fondo negro/transparente.
   - **obs_green**: fondo verde puro `(0, 255, 0)` para chroma key. Asegúrate de configurar el color clave en OBS como verde `(0, 255, 0)`.

### 👾 Créditos
Este proyecto fue desarrollado con amor al fighting 🕹️, mucha paciencia, y la ayuda de ChatGPT, Gemini y Cursor.
