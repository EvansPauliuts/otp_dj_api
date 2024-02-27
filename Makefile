DC = docker-compose

.PHONY: dev test urls pre

pre:
	pre-commit run --all-files

dev:
	$(DC) up -d --build

test:
	$(DC) exec api pytest -rP -vv
	#docker exec -it api pytest api/tests/test_auth.py -k 'verify_account' -rP -vv

urls:
	$(DC) exec api python3 manage.py show_urls
