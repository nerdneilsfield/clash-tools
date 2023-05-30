.PHONY: build
build:
	docker build -t clash_tools .

.PHONY: up
up:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down