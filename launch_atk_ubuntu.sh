#!/usr/bin/env bash
set -euo pipefail

ATK_HOME="${ATK_HOME:-/opt/ATK/ATK-4.0.0}"
ATK_PORT="${ATK_PORT:-6655}"
SYSTEM_GL_PATHS="${SYSTEM_GL_PATHS:-/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu}"
SYSTEM_GL_LIB="${SYSTEM_GL_LIB:-/lib/x86_64-linux-gnu/libGL.so.1}"
MESA_DRI_PATHS="${MESA_DRI_PATHS:-/usr/lib/x86_64-linux-gnu/dri:/lib/x86_64-linux-gnu/dri:/usr/lib/dri}"

export FONTCONFIG_PATH="${FONTCONFIG_PATH:-${ATK_HOME}/fonts}"
export QT_PLUGIN_PATH="${QT_PLUGIN_PATH:-${ATK_HOME}}"
export QT_QPA_PLATFORM_PLUGIN_PATH="${QT_QPA_PLATFORM_PLUGIN_PATH:-${ATK_HOME}/platforms}"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
export QT_XCB_GL_INTEGRATION="${QT_XCB_GL_INTEGRATION:-xcb_glx}"
export QT_OPENGL="${QT_OPENGL:-desktop}"

# Keep ATK's bundled Qt 5.7 libraries ahead of system Qt. Mixing the bundled
# xcb platform plugin with Ubuntu's newer Qt libraries can make Qt report that
# the xcb plugin was found but could not be loaded. Preload only the system GLVND
# libGL to avoid ATK's old bundled libGL.so.1 while preserving Qt compatibility.
export LD_LIBRARY_PATH="${ATK_HOME}:${ATK_HOME}/../lib:${SYSTEM_GL_PATHS}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
if [[ -r "${SYSTEM_GL_LIB}" ]]; then
  export LD_PRELOAD="${SYSTEM_GL_LIB}${LD_PRELOAD:+:${LD_PRELOAD}}"
fi

if [[ "${ATK_SOFTWARE_GL:-0}" == "1" ]]; then
  export QT_OPENGL="${QT_OPENGL:-software}"
  export LIBGL_ALWAYS_SOFTWARE=1
  export MESA_LOADER_DRIVER_OVERRIDE="${MESA_LOADER_DRIVER_OVERRIDE:-llvmpipe}"
  export LIBGL_DRI3_DISABLE=1
  export LIBGL_DRIVERS_PATH="${LIBGL_DRIVERS_PATH:-${MESA_DRI_PATHS}}"
fi

if [[ "${ATK_DEBUG_GL:-0}" == "1" ]]; then
  export LIBGL_DEBUG=verbose
  export QT_DEBUG_PLUGINS=1
fi

cd "${ATK_HOME}"

exec "${ATK_HOME}/ATK" \
  --port "${ATK_PORT}" \
  --hide-startup \
  --hide-welcome \
  --no-crash-report \
  "$@"
