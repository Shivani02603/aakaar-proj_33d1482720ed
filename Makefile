install:
	pip install -r backend/requirements.txt
	npm install --prefix frontend

dev:
	./scripts/dev.sh

build:
	docker-compose build

test:
	pytest backend/tests
	npm test --prefix frontend

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf backend/__pycache__ frontend/node_modules