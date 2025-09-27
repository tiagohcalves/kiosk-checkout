
setup:
	python3 -m venv backend/venv
	pip install -r backend/requirements.txt
	
seed:
	cd backend && PYTHONPATH=. venv/bin/python3 checkout/repository/seed.py seed_data.json

dbshell:
	sqlite3 backend/mashgin.db

run-backend:
	cd backend && PYTHONPATH=. venv/bin/uvicorn checkout.main:app --reload

run-frontend:
	cd frontend && npm start

test-backend:
	cd backend && PYTHONPATH=. venv/bin/pytest tests/ -v

lint-backend:
	cd backend && venv/bin/black checkout tests

# Docker commands
docker-build:
	docker compose build

docker-up:
	docker compose up

docker-up-with-seed:
	docker compose up -d
	docker compose --profile seed up db-seeder

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-clean:
	docker compose down -v
	docker compose build --no-cache

# Quick command to build and run everything with seeding
docker-run: docker-build docker-up-with-seed
	@echo "🚀 Applications are starting up..."
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

start: docker-run