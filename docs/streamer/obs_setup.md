# Checklist OBS (Joystick Overlay)

Pasos concretos para componer el HUD en **OBS Studio** con ventana y chroma. Los modos `normal` / `obs_green` se describen en [Modos de captura y OBS](capture_modes.md).

## Antes de capturar

1. En **Configurar perfiles**, elige **Modo de captura** del perfil activo (`normal` u `obs_green`).
2. Arranca el HUD con ese perfil para que el fondo sea el esperado.

## Fuente de ventana

1. Añade una fuente **Captura de ventana** (o equivalente en tu idioma).
2. Selecciona la ventana de **Joystick Overlay** (el título puede incluir «Torneo» si usas modo torneo).

## Croma con `obs_green`

1. Con el modo `obs_green` (fondo **RGB 0, 255, 0**), añade a esa fuente un filtro **Chroma Key** / **Clave de croma**.
2. Color clave: **verde puro (0, 255, 0)**.
3. Ajusta **similaridad** y reducción de **spill** según iluminación y si hay reflejos verdes en stick o texto.

## Orden de capas

- Coloca el HUD **encima** del juego o escena que quieras mostrar, o debajo según el efecto deseado; el chroma deja transparente el verde solo en esa fuente.
- Si usas `normal` sin croma, el fondo del overlay no es clave uniforme: compón con máscaras o recorte si necesitas aislar elementos.

## Si algo falla

- Comprueba que capturas la **ventana correcta** (no el escritorio entero salvo que quieras).
- Ver [Solución de problemas](../user/troubleshooting.md) (VIDEORESIZE, tiling).

**Más detalles:** [Modos de captura](capture_modes.md), [referencia de layout](../reference/layout_reference.md).
