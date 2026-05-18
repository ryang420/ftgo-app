#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose/docker-compose.yml"
RUNTIME_DIR="$ROOT_DIR/.runtime"
LOG_DIR="$RUNTIME_DIR/logs"
PID_FILE="$RUNTIME_DIR/services.pid"

mkdir -p "$LOG_DIR"

cd "$ROOT_DIR"

if [[ -f "$PID_FILE" ]]; then
  while IFS=: read -r name pid port log_file; do
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "$name is already running on port $port with pid $pid."
      echo "Run 'make dev-down' before starting the stack again."
      exit 1
    fi
  done < "$PID_FILE"
fi

>"$PID_FILE"

stop_started_services() {
  if [[ ! -f "$PID_FILE" ]]; then
    return
  fi

  while IFS=: read -r name pid port log_file; do
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "Stopping $name..."
      kill "$pid" 2>/dev/null || true
    fi
  done < "$PID_FILE"
}

wait_for_health() {
  local name="$1"
  local pid="$2"
  local port="$3"
  local log_file="$4"
  local url="http://localhost:${port}/health"

  for _ in $(seq 1 30); do
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "$name exited before becoming healthy. Last log lines:"
      tail -n 40 "$log_file" || true
      return 1
    fi

    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "$name is healthy at $url"
      return 0
    fi

    sleep 1
  done

  echo "$name did not become healthy at $url. Last log lines:"
  tail -n 40 "$log_file" || true
  return 1
}

start_service() {
  local name="$1"
  local app="$2"
  local port="$3"
  local log_file="$LOG_DIR/${name}.log"

  echo "Starting $name on port $port..."
  nohup uv run uvicorn "$app" --host 0.0.0.0 --port "$port" >"$log_file" 2>&1 &
  local pid=$!
  disown "$pid" 2>/dev/null || true
  echo "$name:$pid:$port:$log_file" >> "$PID_FILE"
  wait_for_health "$name" "$pid" "$port" "$log_file"
}

start_worker() {
  local name="$1"
  local log_file="$LOG_DIR/${name}.log"

  echo "Starting $name..."
  nohup uv run --package order-service python services/order-service/src/order_service/relay.py >"$log_file" 2>&1 &
  local pid=$!
  disown "$pid" 2>/dev/null || true
  echo "$name:$pid:-:$log_file" >> "$PID_FILE"

  sleep 2
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "$name exited during startup. Last log lines:"
    tail -n 40 "$log_file" || true
    return 1
  fi
  echo "$name is running with pid $pid"
}

trap 'echo "Startup failed; stopping services started by this script."; stop_started_services' ERR

echo "Starting Docker infrastructure..."
docker compose -f "$COMPOSE_FILE" up -d

echo "Running database migrations..."
make migrate

start_service "consumer-service" "consumer_service.main:app" "8001"
start_service "restaurant-service" "restaurant_service.main:app" "8002"
start_service "order-service" "order_service.main:app" "8003"
start_service "api-gateway" "api_gateway.main:app" "8000"
start_worker "order-outbox-relay"

trap - ERR

echo ""
echo "FTGO local stack is running."
echo "API gateway: http://localhost:8000"
echo "Order outbox relay: running in background"
echo "Logs: $LOG_DIR"
echo "Stop everything with: make dev-down"
