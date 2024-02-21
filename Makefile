.PHONY: dev test

dev:
	docker-compose up -d --build

test:
	docker exec -it api pytest -rP -vv
	#docker exec -it api pytest api/tests/test_auth.py -k 'verify_account' -rP -vv
