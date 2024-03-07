DC = docker-compose
PC = pip-compile
MG = python src/manage.py

.PHONY: dev test urls pre, test_local test_docker

test_local:
	pytest -rP -vv

test_docker:
	$(DC) exec api pytest -rP -vv

pre:
	pre-commit run --all-files

dev:
	$(DC) up -d --build

test:
	$(DC) exec api pytest -rP -vv
	#docker exec -it api pytest api/tests/test_auth.py -k 'verify_account' -rP -vv

urls:
	$(DC) exec api python3 manage.py show_urls

.PHONY: req_dev peq_prod

req_dev:
	$(PC) ./requirements/dev.in

req_prod:
	$(PC) ./requirements/prod.in

.PHONY: show_urls

show_urls:
	$(MG) show_urls

.PHONY: local_test

local_test:
	pytest -vvv tests/apps/accounts

.PHONY: ruf_format uv_pip pip_install ruff_check chekc_i

ruff_check:
	ruff check --fix .

ruf_format:
	ruff format .

check_i:
	ruff check . --select I --fix
	ruff format .

uv_pip:
	uv pip compile requirements/dev.in -o requirements/dev.txt

pip_install:
	uv pip install -r requirements/dev.txt
