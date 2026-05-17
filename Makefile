COMPOSE_FILE := deploy/docker-compose/docker-compose.yml

.PHONY: help sync infra-up infra-down infra-reset migrate migrate-consumer migrate-restaurant migrate-order run-api-gateway run-consumer run-restaurant run-order

help:
	@echo "FTGO local development commands"
	@echo ""
	@echo "  make sync              Sync all workspace packages"
	@echo "  make infra-up          Start Docker Postgres and RabbitMQ"
	@echo "  make infra-down        Stop Docker infrastructure"
	@echo "  make infra-reset       Stop infrastructure and remove volumes"
	@echo "  make migrate           Run core service database migrations"
	@echo "  make run-consumer      Start consumer-service on port 8001"
	@echo "  make run-restaurant    Start restaurant-service on port 8002"
	@echo "  make run-order         Start order-service on port 8003"
	@echo "  make run-api-gateway   Start api-gateway on port 8000"

sync:
	uv sync --all-packages

infra-up:
	docker compose -f $(COMPOSE_FILE) up -d

infra-down:
	docker compose -f $(COMPOSE_FILE) down

infra-reset:
	docker compose -f $(COMPOSE_FILE) down -v

migrate: migrate-consumer migrate-restaurant migrate-order

migrate-consumer:
	cd services/consumer-service && uv run --package consumer-service alembic -c alembic.ini upgrade head

migrate-restaurant:
	cd services/restaurant-service && uv run --package restaurant-service alembic -c alembic.ini upgrade head

migrate-order:
	cd services/order-service && uv run --package order-service alembic -c alembic.ini upgrade head

run-consumer:
	uv run uvicorn consumer_service.main:app --port 8001

run-restaurant:
	uv run uvicorn restaurant_service.main:app --port 8002

run-order:
	uv run uvicorn order_service.main:app --port 8003

run-api-gateway:
	uv run uvicorn api_gateway.main:app --port 8000
