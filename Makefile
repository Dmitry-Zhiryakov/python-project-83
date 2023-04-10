install:
	poetry install

db-create:
	createdb page_analyzer

schema-load:
	psql page_analyzer < database.sql

lint:
	poetry run flake8 page_analyzer

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

.PHONY: install db-create schema-load lint dev start