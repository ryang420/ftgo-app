#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATEWAY_URL="${FTGO_API_GATEWAY_URL:-http://localhost:8000}"
COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose/docker-compose.yml"

cd "$ROOT_DIR"

json_value() {
  local expression="$1"
  python -c "import json, sys; data = json.load(sys.stdin); print(${expression})"
}

echo "Running place order demo..."
demo_output="$(make demo-place-order)"
printf '%s\n' "$demo_output"

order_json="$(DEMO_OUTPUT="$demo_output" python - <<'PY'
import json
import os
import sys

text = os.environ["DEMO_OUTPUT"]
start = text.rfind("\n{")
if start == -1:
    start = text.find("{")
if start == -1:
    raise SystemExit("Could not find order JSON in demo output")
print(text[start:].strip())
PY
)"
order_id="$(printf '%s' "$order_json" | json_value "data['id']")"
echo "Waiting for kitchen ticket for order ${order_id}..."

ticket_json=""
for _ in $(seq 1 20); do
  tickets="$(curl -fsS "${GATEWAY_URL}/kitchen/tickets")"
  ticket_json="$(
    TICKETS="$tickets" python - "$order_id" <<'PY'
import json
import os
import sys

order_id = sys.argv[1]
tickets = json.loads(os.environ["TICKETS"])
for ticket in tickets:
    if ticket["order_id"] == order_id:
        print(json.dumps(ticket))
        break
PY
  )"
  if [[ -n "$ticket_json" ]]; then
    break
  fi
  sleep 1
done

if [[ -z "$ticket_json" ]]; then
  echo "Kitchen ticket was not created for order ${order_id}."
  exit 1
fi

echo "Kitchen ticket created:"
printf '%s' "$ticket_json" | python -m json.tool

published_query="
select published_at is not null
from outbox_messages
where aggregate_id = '${order_id}'
  and event_type = 'OrderCreated'
order by created_at desc
limit 1
"
published="$(
  docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U ftgo -d order_db -tAc "$published_query"
)"

if [[ "$published" != "t" ]]; then
  echo "OrderCreated outbox message for ${order_id} was not published."
  exit 1
fi

echo "OrderCreated outbox message was published."
echo "Waiting for order approval..."

order_status=""
for _ in $(seq 1 20); do
  order_response="$(curl -fsS "${GATEWAY_URL}/orders/${order_id}")"
  order_status="$(printf '%s' "$order_response" | json_value "data['status']")"
  if [[ "$order_status" == "APPROVED" ]]; then
    break
  fi
  sleep 1
done

if [[ "$order_status" != "APPROVED" ]]; then
  echo "Order ${order_id} did not transition to APPROVED. Last status: ${order_status}"
  exit 1
fi

ticket_id="$(printf '%s' "$ticket_json" | json_value "data['id']")"
kitchen_published_query="
select published_at is not null
from outbox_messages
where aggregate_id = '${ticket_id}'
  and event_type = 'KitchenTicketCreated'
order by created_at desc
limit 1
"
kitchen_published="$(
  docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U ftgo -d kitchen_db -tAc "$kitchen_published_query"
)"

if [[ "$kitchen_published" != "t" ]]; then
  echo "KitchenTicketCreated outbox message for ${ticket_id} was not published."
  exit 1
fi

echo "KitchenTicketCreated outbox message was published."
echo "Order transitioned to APPROVED."
echo "E2E place order flow passed."
