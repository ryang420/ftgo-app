#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose/docker-compose.yml"
RUNTIME_DIR="$ROOT_DIR/.runtime"
PID_FILE="$RUNTIME_DIR/services.pid"

cd "$ROOT_DIR"

if [[ -f "$PID_FILE" ]]; then
  while IFS=: read -r name pid port log_file; do
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "Stopping $name on port $port with pid $pid..."
      kill "$pid" 2>/dev/null || true
    else
      echo "$name is not running."
    fi
  done < "$PID_FILE"

  for _ in $(seq 1 10); do
    still_running=0
    while IFS=: read -r name pid port log_file; do
      if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
        still_running=1
      fi
    done < "$PID_FILE"

    if [[ "$still_running" -eq 0 ]]; then
      break
    fi

    sleep 1
  done

  while IFS=: read -r name pid port log_file; do
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "Force stopping $name with pid $pid..."
      kill -9 "$pid" 2>/dev/null || true
    fi
  done < "$PID_FILE"

  rm -f "$PID_FILE"
else
  echo "No tracked app services are running."
fi

echo "Stopping Docker infrastructure..."
docker compose -f "$COMPOSE_FILE" down

echo "FTGO local stack is stopped."
