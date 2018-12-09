dev:
	docker-compose -f devops/docker-compose-dev.yml up --build

test:
	docker-compose -f devops/docker-compose-dev.yml run dalite pytest --cov
