.PHONY: up down logs build alembic-current alembic-upgrade alembic-revision

COMPOSE := docker compose -f docker/docker-compose.yml

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

alembic-current:
	alembic current

alembic-upgrade:
	alembic upgrade head

# Usage: make alembic-revision MSG="add_users_table"
MSG ?= "migration"
alembic-revision:
	alembic revision --autogenerate -m "$(MSG)"

