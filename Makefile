
setup:
	python3 -m venv backend/venv
	pip install -r backend/requirements.txt

venv:
	. backend/venv/bin/activate
	
seed: venv
	cd backend && PYTHONPATH=. python3 checkout/repository/seed.py seed_data.json

dbshell:
	sqlite3 backend/mashgin.db

run-backend: venv
	cd backend && PYTHONPATH=. uvicorn checkout.main:app --reload

run-frontend:
	cd frontend && npm start

test-backend: venv
	cd backend && PYTHONPATH=. pytest tests/ -v