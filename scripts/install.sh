#!/usr/bin/env bash

set -u

SCRIPT_PATH="$(readlink -f "$0")"
BASE_DIR="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
cd "$BASE_DIR" || exit 1
chmod +x "$BASE_DIR/scripts/run.sh" "$BASE_DIR/install.sh" "$BASE_DIR/scripts/install.sh" "$BASE_DIR/scripts/update.sh" 2>/dev/null || true

ensure_venv() {
	if [ ! -d "$BASE_DIR/venv" ]; then
		echo "Creando entorno virtual en $BASE_DIR/venv ..."
		python3 -m venv "$BASE_DIR/venv" || return 1
	fi
	"$BASE_DIR/venv/bin/python3" -m pip install --upgrade pip
	"$BASE_DIR/venv/bin/python3" -m pip install -r "$BASE_DIR/requirements.txt"
	if [ "${JOYSTICK_SKIP_PIP_EDITABLE:-0}" != "1" ]; then
		if [ -f "$BASE_DIR/pyproject.toml" ]; then
			echo "Instalando proyecto en modo editable (pip install -e .) ..."
			"$BASE_DIR/venv/bin/python3" -m pip install -e "$BASE_DIR" || echo "[WARN] pip install -e . fallo; puedes omitir con JOYSTICK_SKIP_PIP_EDITABLE=1"
		fi
	fi
}

offer_copy_docs() {
	if [ "${JOYSTICK_SKIP_DOC_COPY:-0}" = "1" ]; then
		return 0
	fi
	local doc_dest="${HOME}/.local/share/doc/joystick-overlay"
	echo ""
	echo "¿Copiar la documentacion Markdown a ${doc_dest}? (s/n)"
	echo "s: copia el contenido de docs/ (referencia en tu HOME; puedes repetir para actualizar)."
	echo "n: omitir."
	printf "Copiar documentacion (s/n): "
	read -r doc_answer
	if [ "$doc_answer" = "s" ] || [ "$doc_answer" = "S" ]; then
		if mkdir -p "$doc_dest" && cp -a "${BASE_DIR}/docs/." "${doc_dest}/"; then
			echo "Documentacion copiada en: $doc_dest"
		else
			echo "[WARN] No se pudo copiar la documentacion."
		fi
	fi
}

ensure_launcher_parent_dir() {
	local launcher_path="$1"
	local parent_dir
	parent_dir="$(dirname "$launcher_path")"
	if [ "$use_sudo" -eq 1 ]; then
		if mkdir -p "$parent_dir" 2>/dev/null; then
			return 0
		fi
		if command -v sudo >/dev/null 2>&1; then
			sudo mkdir -p "$parent_dir"
			return $?
		fi
		return 1
	fi
	mkdir -p "$parent_dir"
}

write_desktop_file() {
	local desktop_path="$1"
	local app_name="$2"
	local app_exec="$3"
	local app_categories="$4"
	local app_icon="$5"
	local terminal_value="$6"
	{
		echo "[Desktop Entry]"
		echo "Name=$app_name"
		echo "Comment=Joystick Overlay — Arcade input viewer"
		echo "Exec=$app_exec"
		if [ -n "$app_icon" ]; then
			echo "Icon=$app_icon"
		fi
		echo "Terminal=$terminal_value"
		echo "Type=Application"
		echo "Categories=$app_categories"
	} > "$desktop_path"
}

install_desktop_entries() {
	local launcher_path="$1"
	local app_dir="$HOME/.local/share/applications"
	local icon_dir="$HOME/.local/share/icons"
	local icon_source=""
	local icon_target=""
	local terminal_value="false"

	if [ "${JOYSTICK_DESKTOP_TERMINAL:-0}" = "1" ]; then
		terminal_value="true"
	fi

	if [ -f "$BASE_DIR/install/icon.ico" ]; then
		icon_source="$BASE_DIR/install/icon.ico"
		icon_target="$icon_dir/joystick-overlay.ico"
	elif [ -f "$BASE_DIR/install/joystick_overlay.ico" ]; then
		icon_source="$BASE_DIR/install/joystick_overlay.ico"
		icon_target="$icon_dir/joystick-overlay.ico"
	elif [ -f "$BASE_DIR/install/joystick-overlay.png" ]; then
		icon_source="$BASE_DIR/install/joystick-overlay.png"
		icon_target="$icon_dir/joystick-overlay.png"
	elif [ -f "$BASE_DIR/icons/joystick-overlay.png" ]; then
		icon_source="$BASE_DIR/icons/joystick-overlay.png"
		icon_target="$icon_dir/joystick-overlay.png"
	fi

	mkdir -p "$app_dir"
	mkdir -p "$icon_dir"
	if [ -n "$icon_source" ] && [ -n "$icon_target" ]; then
		cp "$icon_source" "$icon_target"
	fi

	write_desktop_file \
		"$app_dir/joystick-overlay.desktop" \
		"Joystick Overlay" \
		"$launcher_path" \
		"Game;" \
		"$icon_target" \
		"$terminal_value"
	write_desktop_file \
		"$app_dir/joystick-overlay-config.desktop" \
		"Joystick Overlay Config" \
		"$launcher_path config" \
		"Settings;Utility;" \
		"$icon_target" \
		"$terminal_value"
	write_desktop_file \
		"$app_dir/joystick-overlay-tournament.desktop" \
		"Joystick Overlay Tournament" \
		"$launcher_path tournament" \
		"Game;" \
		"$icon_target" \
		"$terminal_value"
}

echo "Instalador Joystick Overlay"
echo "Ruta del proyecto: $BASE_DIR"
if [ ! -f "$BASE_DIR/arcade/assets/.assets_version" ]; then
	echo "Error: falta arcade/assets/.assets_version (assets inválidos)."
	exit 1
fi
if [ ! -d "$BASE_DIR/arcade/assets/icon_packs" ]; then
	echo "Error: falta arcade/assets/icon_packs (assets incompletos)."
	exit 1
fi
if ! ensure_venv; then
	echo "Error al preparar el entorno virtual."
	exit 1
fi

offer_copy_docs

echo ""
echo "¿Deseas instalar Joystick Overlay tipo aplicación? (n/s)"
echo "n: gracias por usar Joystick Overlay, que tengas excelente día."
echo "s: se instalara launcher y accesos del menu"
printf "Selecciona (n/s): "
read -r answer

if [ "$answer" = "n" ] || [ "$answer" = "N" ]; then
	echo "Gracias por usar Joystick Overlay. Saludos."
	exit 0
fi

if [ "$answer" != "s" ] && [ "$answer" != "S" ]; then
	echo "Opción no válida. Fin de instalación."
	exit 0
fi

detected_graphics_server=""
if [ -n "${WAYLAND_DISPLAY:-}" ]; then
	detected_graphics_server="wayland"
elif [ -n "${DISPLAY:-}" ]; then
	detected_graphics_server="x11"
elif [ "${XDG_SESSION_TYPE:-}" = "wayland" ] || [ "${XDG_SESSION_TYPE:-}" = "x11" ]; then
	detected_graphics_server="${XDG_SESSION_TYPE:-}"
fi

if [ -n "${JOYSTICK_OVERLAY_ASSUME_GRAPHICS:-}" ]; then
	echo ""
	echo "JOYSTICK_OVERLAY_ASSUME_GRAPHICS está definida (valor: ${JOYSTICK_OVERLAY_ASSUME_GRAPHICS})."
	if [ "${JOYSTICK_OVERLAY_ASSUME_GRAPHICS}" = "1" ]; then
		detected_graphics_server="${detected_graphics_server:-assumed}"
		echo "Omitiendo detección interactiva de entorno gráfico."
	else
		echo "Solo el valor 1 omite esa detección; se continúa con el flujo normal."
	fi
fi

if [ -n "${DISPLAY:-}" ] && [ "${JOYSTICK_OVERLAY_ASSUME_GRAPHICS:-0}" != "1" ]; then
	if command -v xdpyinfo >/dev/null 2>&1; then
		if ! xdpyinfo >/dev/null 2>&1; then
			detected_graphics_server=""
			echo ""
			echo "DISPLAY está presente pero no se pudo validar con xdpyinfo."
		fi
	else
		echo ""
		echo "xdpyinfo no está instalado; se omite validación extra de DISPLAY (solo variable de entorno)."
	fi
fi

if [ -n "$detected_graphics_server" ]; then
	echo ""
	echo "Sesión gráfica detectada automáticamente: $detected_graphics_server"
else
	echo ""
	echo "No se detectó sesión/servidor gráfico automáticamente."
	echo "¿Está en un entorno gráfico? (s/n)"
	printf "Selecciona (s/n): "
	read -r in_graphic_env
	if [ "$in_graphic_env" = "n" ] || [ "$in_graphic_env" = "N" ]; then
		echo "No se detecta uso de entorno gráfico."
		echo "Abre una sesión gráfica (X11 o Wayland) y vuelve a ejecutar install.sh."
		exit 0
	fi
	if [ "$in_graphic_env" != "s" ] && [ "$in_graphic_env" != "S" ]; then
		echo "Opción no válida. Fin de instalación."
		exit 0
	fi

	echo ""
	echo "¿Qué servidor gráfico usa?"
	echo "1) X11"
	echo "2) Wayland"
	echo "3) Otro / no estoy seguro"
	printf "Selecciona (1/2/3): "
	read -r graphic_server
	if [ "$graphic_server" = "1" ]; then
		detected_graphics_server="x11"
		echo "Servidor seleccionado: X11."
	elif [ "$graphic_server" = "2" ]; then
		detected_graphics_server="wayland"
		echo "Servidor seleccionado: Wayland."
	else
		detected_graphics_server="otro"
		echo "Servidor seleccionado: Otro / no definido."
	fi

	echo ""
	echo "Advertencia:"
	echo "En algunos entornos gráficos el overlay puede no funcionar correctamente."
	echo "Si notas fallos visuales, prueba sesión X11 y revisa joystick-overlay doctor."
	printf "¿Deseas continuar de todos modos? (s/n): "
	read -r continue_after_warning
	if [ "$continue_after_warning" != "s" ] && [ "$continue_after_warning" != "S" ]; then
		echo "Instalación cancelada por usuario."
		exit 0
	fi
fi

launcher_target="$HOME/.local/bin/joystick-overlay"
use_sudo=0
echo ""
echo "¿Instalación global en /usr/local/bin? (s/n, default n)"
printf "Selecciona (s/n): "
read -r global_choice
if [ "$global_choice" = "s" ] || [ "$global_choice" = "S" ]; then
	launcher_target="/usr/local/bin/joystick-overlay"
	use_sudo=1
fi

echo ""
echo "Se va a instalar:"
echo "- Launcher: $launcher_target -> $BASE_DIR/scripts/run.sh"
echo "- Desktop: ~/.local/share/applications/*.desktop"
if [ -f "$BASE_DIR/install/icon.ico" ] || [ -f "$BASE_DIR/install/joystick_overlay.ico" ] || [ -f "$BASE_DIR/install/joystick-overlay.png" ] || [ -f "$BASE_DIR/icons/joystick-overlay.png" ]; then
	echo "- Icono: ~/.local/share/icons/joystick-overlay.(ico|png)"
else
	echo "- Icono: omitido (agrega install/icon.ico o install/joystick_overlay.ico)"
fi
printf "Confirmar instalación (s/n): "
read -r confirm
if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
	echo "Instalación cancelada por usuario."
	exit 0
fi

if ! ensure_launcher_parent_dir "$launcher_target"; then
	echo "No se pudo preparar directorio de launcher: $(dirname "$launcher_target")"
	exit 1
fi
if [ "$use_sudo" -eq 1 ]; then
	if ln -sf "$BASE_DIR/scripts/run.sh" "$launcher_target" 2>/dev/null; then
		:
	elif command -v sudo >/dev/null 2>&1; then
		if ! sudo ln -sf "$BASE_DIR/scripts/run.sh" "$launcher_target"; then
			echo "No se pudo instalar launcher global."
			exit 1
		fi
	else
		echo "No hay permisos para instalar en /usr/local/bin y sudo no está disponible."
		exit 1
	fi
else
	if ! ln -sf "$BASE_DIR/scripts/run.sh" "$launcher_target"; then
		echo "No se pudo instalar launcher en $launcher_target."
		exit 1
	fi
fi

if ! install_desktop_entries "$launcher_target"; then
	echo "No se pudieron copiar los archivos .desktop."
	exit 1
fi

echo ""
echo "Instalación completa."
echo "Launcher instalado en: $launcher_target"
echo "Puedes abrir:"
echo "- joystick-overlay"
echo "- joystick-overlay config"
echo "- joystick-overlay tournament"
echo "- joystick-overlay --help"
echo ""
echo "También puedes buscar 'Joystick Overlay' en tu menú de aplicaciones."
if command -v update-desktop-database >/dev/null 2>&1; then
	echo "Si no aparece en el menú, ejecuta:"
	echo "  update-desktop-database ~/.local/share/applications"
	echo "O reinicia tu sesión gráfica."
else
	echo "Si no aparece en el menú, reinicia tu sesión gráfica."
fi
if [ "$launcher_target" = "$HOME/.local/bin/joystick-overlay" ]; then
	echo ""
	echo "Si joystick-overlay no existe en terminal, añade ~/.local/bin al PATH."
fi
