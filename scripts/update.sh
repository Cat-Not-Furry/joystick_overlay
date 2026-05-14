#!/usr/bin/env bash

set -u

SCRIPT_PATH="$(readlink -f "$0")"
BASE_DIR="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
cd "$BASE_DIR" || exit 1
# Canon alineado con config.py: PROJECT_ROOT/user (no XDG como datos operativos).
USER_DIR="$BASE_DIR/user"
UPDATE_LOG="$USER_DIR/update.log"
ASSETS_DIR="$BASE_DIR/arcade/assets"
ASSETS_VERSION_FILE="$ASSETS_DIR/.assets_version"

log_line() {
	local action="$1"
	local result="$2"
	local message="$3"
	local ts
	ts="$(date '+%Y-%m-%dT%H:%M:%S')"
	mkdir -p "$USER_DIR"
	echo "$ts | $action | $result | $message" >> "$UPDATE_LOG"
}

log_start() {
	echo "== Joystick Overlay update =="
	echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
	echo "Base: $BASE_DIR"
	log_line "start" "INFO" "base=$BASE_DIR"
}

validate_assets_structure() {
	local root="$1"
	if [ ! -f "$root/arcade/assets/.assets_version" ]; then
		log_line "validate" "ERROR" "missing arcade/assets/.assets_version"
		return 1
	fi
	if [ ! -d "$root/arcade/assets/icon_packs" ]; then
		log_line "validate" "ERROR" "missing arcade/assets/icon_packs"
		return 1
	fi
	return 0
}

update_from_git_code() {
	if [ ! -d "$BASE_DIR/.git" ]; then
		echo "No se detecto repositorio git en $BASE_DIR"
		log_line "git_pull" "ERROR" "missing .git"
		return 1
	fi

	if ! command -v git >/dev/null 2>&1; then
		echo "git no esta disponible en el sistema."
		log_line "git_pull" "ERROR" "git missing"
		return 1
	fi

	if ! git pull --ff-only; then
		echo "No se pudo actualizar con git pull --ff-only."
		log_line "git_pull" "ERROR" "git pull failed"
		return 1
	fi
	log_line "git_pull" "SUCCESS" "git pull --ff-only"
	return 0
}

copy_whitelist_from_zip_dir() {
	local src_dir="$1"
	local dst_dir="$2"
	local items=(
		"arcade"
		"configs"
		"main.py"
		"configure.py"
		"tournament.py"
		"cli.py"
		"doctor.py"
		"engine_sys_path.py"
		"scripts"
		"README.md"
		"docs"
	)
	if [ ! -f "$src_dir/main.py" ]; then
		echo "ZIP invalido: no contiene main.py en la raiz esperada."
		log_line "zip_validate" "ERROR" "main.py missing"
		return 1
	fi
	local item
	for item in "${items[@]}"; do
		if [ -e "$src_dir/$item" ]; then
			cp -rL "$src_dir/$item" "$dst_dir/"
		fi
	done
	return 0
}

validate_extracted_tree_safe() {
	local root="$1"
	if [ -z "$root" ] || [ ! -d "$root" ]; then
		log_line "zip_scan" "ERROR" "scan root missing"
		return 1
	fi
	if [ -n "$(find -P "$root" -type l -print -quit 2>/dev/null)" ]; then
		echo "ZIP invalido: enlaces simbolicos no permitidos en el arbol extraido."
		log_line "zip_scan" "ERROR" "symlink in tree"
		return 1
	fi
	if [ -n "$(find -P "$root" ! -type f ! -type d -print -quit 2>/dev/null)" ]; then
		echo "ZIP invalido: tipos de fichero no permitidos (socket/FIFO/dispositivo)."
		log_line "zip_scan" "ERROR" "non-file non-dir in tree"
		return 1
	fi
	return 0
}

update_from_zip() {
	local zip_path="$1"
	if [ -z "$zip_path" ]; then
		echo "Falta ruta de ZIP. Uso: ./update.sh --zip /ruta/release.zip"
		return 1
	fi
	if [ ! -f "$zip_path" ]; then
		echo "No existe ZIP: $zip_path"
		return 1
	fi
	mkdir -p "$USER_DIR"
	local flock_rc=0
	(
		flock -n 200 || exit 7
		local tmp_dir assets_tmp
		tmp_dir="$(mktemp -d /tmp/joystick_overlay_zip_update_XXXXXX)"
		assets_tmp="$(mktemp -d /tmp/joystick_overlay_assets_XXXXXX)"
		if ! unzip -q "$zip_path" -d "$tmp_dir"; then
			echo "No se pudo descomprimir ZIP."
			log_line "zip_unpack" "ERROR" "unzip failed"
			rm -rf "$tmp_dir" "$assets_tmp"
			exit 1
		fi
		local extracted_root=""
		extracted_root="$(ls -1d "$tmp_dir"/*/ 2>/dev/null | sed -n '1p')"
		extracted_root="${extracted_root%/}"
		if [ -z "$extracted_root" ]; then
			echo "ZIP inválido: estructura no reconocida."
			log_line "zip_unpack" "ERROR" "invalid zip structure"
			rm -rf "$tmp_dir" "$assets_tmp"
			exit 1
		fi
		if ! validate_assets_structure "$extracted_root"; then
			echo "ZIP invalido: assets incompletos."
			rm -rf "$tmp_dir" "$assets_tmp"
			exit 1
		fi
		if ! validate_extracted_tree_safe "$extracted_root"; then
			rm -rf "$tmp_dir" "$assets_tmp"
			exit 1
		fi
		cp -rL "$extracted_root/arcade/assets/." "$assets_tmp/"
		if ! copy_whitelist_from_zip_dir "$extracted_root" "$BASE_DIR"; then
			log_line "zip_copy" "ERROR" "whitelist copy failed"
			rm -rf "$tmp_dir" "$assets_tmp"
			exit 1
		fi
		if [ -d "$ASSETS_DIR" ]; then
			rm -rf "$ASSETS_DIR.previous"
			mv "$ASSETS_DIR" "$ASSETS_DIR.previous"
		fi
		mv "$assets_tmp" "$ASSETS_DIR"
		if [ ! -f "$ASSETS_VERSION_FILE" ]; then
			echo "Update fallo: assets sin version tras reemplazo."
			log_line "zip_assets" "ERROR" "assets invalid after replace; rollback"
			rm -rf "$ASSETS_DIR"
			if [ -d "$ASSETS_DIR.previous" ]; then
				mv "$ASSETS_DIR.previous" "$ASSETS_DIR"
			fi
			rm -rf "$tmp_dir"
			exit 1
		fi
		rm -rf "$ASSETS_DIR.previous" "$tmp_dir"
		log_line "zip_update" "SUCCESS" "zip update completed"
		exit 0
	) 200>>"$USER_DIR/update.lock" || flock_rc=$?
	if [ "${flock_rc:-0}" -eq 7 ]; then
		echo "Otro proceso esta actualizando desde ZIP (bloqueo: $USER_DIR/update.lock)."
		log_line "zip_lock" "ERROR" "flock busy"
		return 1
	fi
	if [ "${flock_rc:-0}" -ne 0 ]; then
		return 1
	fi
	return 0
}

if [ ! -x "$BASE_DIR/venv/bin/python3" ]; then
	echo "No existe venv listo. Ejecuta install.sh primero."
	log_line "venv_check" "ERROR" "venv missing"
	exit 1
fi

log_start
mode="${1:-git}"
if [ "$mode" = "--zip" ]; then
	if ! update_from_zip "${2:-}"; then
		log_line "finish" "ERROR" "zip mode failed"
		exit 1
	fi
else
	if ! update_from_git_code; then
		log_line "finish" "ERROR" "git mode failed"
		exit 1
	fi
fi

if ! "$BASE_DIR/venv/bin/python3" -m pip install -r "$BASE_DIR/requirements.txt"; then
	echo "No se pudieron actualizar dependencias."
	log_line "pip_install" "ERROR" "pip install failed"
	exit 1
fi

log_line "pip_install" "SUCCESS" "requirements updated"
log_line "finish" "SUCCESS" "update completed"
echo "Actualización completada."
