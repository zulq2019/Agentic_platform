.PHONY: dev-up dev-down dev-logs lint test scaffold compose dev-status

dev-up: compose
	docker compose up -d --build
	python scripts/wait_for_health.py
	python scripts/verify_dev_environment.py

dev-down:
	docker compose down -v

dev-logs:
	docker compose logs -f

dev-status:
	python scripts/wait_for_health.py
	python scripts/verify_dev_environment.py

compose:
	python scripts/generate_prometheus_config.py
	python scripts/generate_docker_compose.py

scaffold:
	python scripts/scaffold_pi01_services.py

lint:
	ruff check src/shared/aep_common src/platform
	black --check src/shared/aep_common src/platform

test:
	pip install -e "src/shared/aep_common[health]" pytest pytest-asyncio httpx "fastapi>=0.110.0" pytest-cov
	python scripts/run_tests.py
	python -m pytest src/tests -m "story_us_01_01 and not integration and not e2e" -v --cov=aep_common --cov-fail-under=80

migrate:
	pip install -r requirements-dev.txt
	pip install -e "src/shared/aep_common[health]"
	python scripts/run_migrations.py
