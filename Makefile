DC=docker compose

COMPOSE_FILE=docker-compose.yml
COMPOSE_DEV_FILE=docker-compose.dev.yml

SERVICE=ai_star_tg_bot

.PHONY: help up down restart build rebuild logs shell dev dev-build dev-rebuild clean ps

help:
	@echo "Available commands:"
	@echo "  make up           - Start production"
	@echo "  make build        - Build production"
	@echo "  make rebuild      - Rebuild production (no cache)"
	@echo "  make down         - Stop production"
	@echo "  make restart      - Restart production"
	@echo "  make logs         - Production logs"
	@echo "  make shell        - Enter production container"
	@echo ""
	@echo "  make dev          - Start development"
	@echo "  make dev-build    - Build development"
	@echo "  make dev-rebuild  - Rebuild development (no cache)"
	@echo "  make dev-down     - Stop development"
	@echo "  make dev-logs     - Development logs"
	@echo ""
	@echo "  make clean        - Remove containers, volumes, images"
	@echo "  make ps           - Show running containers"

# ---------- PRODUCTION ----------

up:
	$(DC) -f $(COMPOSE_FILE) up -d

build:
	$(DC) -f $(COMPOSE_FILE) build

rebuild:
	$(DC) -f $(COMPOSE_FILE) build --no-cache

down:
	$(DC) -f $(COMPOSE_FILE) down

restart:
	$(DC) -f $(COMPOSE_FILE) down
	$(DC) -f $(COMPOSE_FILE) up -d

logs:
	$(DC) -f $(COMPOSE_FILE) logs -f

shell:
	$(DC) -f $(COMPOSE_FILE) exec $(SERVICE) sh

# ---------- DEVELOPMENT ----------

dev-up:
	$(DC) -f $(COMPOSE_DEV_FILE) up

dev-build:
	$(DC) -f $(COMPOSE_DEV_FILE) build

dev-rebuild:
	$(DC) -f $(COMPOSE_DEV_FILE) build --no-cache

dev-down:
	$(DC) -f $(COMPOSE_DEV_FILE) down

dev-logs:
	$(DC) -f $(COMPOSE_DEV_FILE) logs -f

# ---------- UTILITIES ----------

ps:
	$(DC) ps

clean:
	$(DC) down -v --rmi all --remove-orphans