#!/usr/bin/env bash
set -euo pipefail

GATEWAY_URL="${FTGO_API_GATEWAY_URL:-http://localhost:8000}"
RUN_ID="$(date +%s)"

post_json() {
  local path="$1"
  local payload="$2"

  curl -fsS -X POST "${GATEWAY_URL}${path}" \
    -H "content-type: application/json" \
    -d "$payload"
}

json_value() {
  local expression="$1"
  python -c "import json, sys; data = json.load(sys.stdin); print(${expression})"
}

echo "Creating consumer through ${GATEWAY_URL}..."
consumer_response="$(
  post_json "/consumers" "{
    \"email\": \"alice.${RUN_ID}@example.com\",
    \"first_name\": \"Alice\",
    \"last_name\": \"Wang\",
    \"phone_number\": \"+8613800000000\",
    \"addresses\": [{
      \"label\": \"home\",
      \"street1\": \"123 Main St\",
      \"city\": \"Shanghai\",
      \"state\": \"Shanghai\",
      \"postal_code\": \"200000\",
      \"country\": \"CN\"
    }]
  }"
)"
consumer_id="$(printf '%s' "$consumer_response" | json_value "data['id']")"
echo "Consumer created: ${consumer_id}"

echo "Creating restaurant and menu..."
restaurant_response="$(
  post_json "/restaurants" "{
    \"name\": \"Noodle House ${RUN_ID}\",
    \"slug\": \"noodle-house-${RUN_ID}\",
    \"cuisine\": \"Chinese\",
    \"menu_items\": [{
      \"name\": \"Beef Noodles\",
      \"description\": \"Classic bowl\",
      \"price\": \"28.00\"
    }]
  }"
)"
restaurant_id="$(printf '%s' "$restaurant_response" | json_value "data['id']")"
menu_item_id="$(printf '%s' "$restaurant_response" | json_value "data['menu_items'][0]['id']")"
echo "Restaurant created: ${restaurant_id}; menu item: ${menu_item_id}"

echo "Creating order..."
order_response="$(
  post_json "/orders" "{
    \"consumer_id\": \"${consumer_id}\",
    \"restaurant_id\": ${restaurant_id},
    \"currency\": \"USD\",
    \"line_items\": [{
      \"menu_item_id\": ${menu_item_id},
      \"quantity\": 2
    }]
  }"
)"

echo ""
echo "Place order demo completed:"
printf '%s' "$order_response" | python -m json.tool
