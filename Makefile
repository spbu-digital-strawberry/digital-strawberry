test_unit:
	python -m pytest tests/unit

setup_infra_for_e2e:
	docker compose --profile e2e up -d

test_e2e:
	python -m pytest tests/e2e

start:
	docker compose --profile all up -d

stop:
	docker compose --profile all down
