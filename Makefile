.PHONY: build
build:
	docker-compose build -t clash_tools .

.PHONY: up
up:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down