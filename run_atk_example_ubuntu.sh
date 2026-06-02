#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${ATK_SDK_LOG_DIR:-${SCRIPT_DIR}/logs}"
ATK_PORT="${ATK_PORT:-6655}"
JAVA_PORT="${JAVA_PORT:-8080}"
JAVA_JAR="${SCRIPT_DIR}/java service/atk_python_sdk_service.jar"
JAVA_START="${SCRIPT_DIR}/java service/start.sh"
ATK_START="${SCRIPT_DIR}/launch_atk_ubuntu.sh"
RESTART_JAVA="${ATK_RESTART_JAVA:-1}"

mkdir -p "${LOG_DIR}"

usage() {
  cat <<'EOF'
Usage:
  ./run_atk_example_ubuntu.sh --list
  ./run_atk_example_ubuntu.sh simple [example options]
  ./run_atk_example_ubuntu.sh huge_constellation --no-save

This wrapper keeps the user-facing workflow simple:
  - starts ATK if port 6655 is not listening;
  - restarts the Java bridge by default to clear stale ATK socket state;
  - starts the Java bridge if port 8080 is not listening;
  - runs examples/run_example.py with a fresh Java -> ATK connection;
  - keeps ATK open after the example finishes.

Environment overrides:
  ATK_PORT=6655
  JAVA_PORT=8080
  ATK_RESTART_JAVA=0      Do not restart Java before each example
  ATK_SDK_LOG_DIR=logs    Runtime logs directory
EOF
}

port_listening() {
  local port="$1"
  ss -ltn "sport = :${port}" | grep -q ":${port}"
}

wait_for_port() {
  local port="$1"
  local name="$2"
  local timeout_seconds="$3"

  for _ in $(seq 1 "${timeout_seconds}"); do
    if port_listening "${port}"; then
      return 0
    fi
    sleep 1
  done

  echo "${name} did not start within ${timeout_seconds}s; check ${LOG_DIR}." >&2
  return 1
}

stop_java_bridge() {
  if port_listening "${JAVA_PORT}"; then
    pkill -f "${JAVA_JAR}" || true
    for _ in $(seq 1 10); do
      if ! port_listening "${JAVA_PORT}"; then
        return 0
      fi
      sleep 1
    done
    echo "Java bridge port ${JAVA_PORT} is still in use after stop attempt." >&2
    return 1
  fi
}

start_atk_if_needed() {
  if port_listening "${ATK_PORT}"; then
    echo "ATK is already listening on port ${ATK_PORT}."
    return 0
  fi

  echo "Starting ATK on port ${ATK_PORT}..."
  ATK_PORT="${ATK_PORT}" nohup "${ATK_START}" > "${LOG_DIR}/atk.log" 2>&1 &
  wait_for_port "${ATK_PORT}" "ATK" 30
}

start_java_bridge() {
  echo "Starting Java bridge on port ${JAVA_PORT}..."
  nohup bash "${JAVA_START}" > "${LOG_DIR}/java-service.log" 2>&1 &
  wait_for_port "${JAVA_PORT}" "Java bridge" 20
}

ensure_java_bridge() {
  if [[ "${RESTART_JAVA}" == "1" ]]; then
    stop_java_bridge
    start_java_bridge
    return 0
  fi

  if port_listening "${JAVA_PORT}"; then
    echo "Java bridge is already listening on port ${JAVA_PORT}."
    return 0
  fi

  start_java_bridge
}

if [[ $# -eq 0 ]]; then
  usage
  exit 0
fi

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  --list)
    cd "${SCRIPT_DIR}"
    exec python3 examples/run_example.py --list
    ;;
esac

start_atk_if_needed
ensure_java_bridge

cd "${SCRIPT_DIR}"
exec python3 examples/run_example.py "$@"
