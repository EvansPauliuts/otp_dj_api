DC = docker-compose
PC = pip-compile

.PHONY: dev test urls pre, test_local

test_local:
	pytest -rP -vv

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
