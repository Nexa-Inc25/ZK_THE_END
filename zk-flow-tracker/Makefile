PY=python3
PIP=pip
UVICORN=uvicorn

install:
	$(PIP) install -r requirements.txt

up:
	docker compose up -d db redis

down:
	docker compose down

api:
	$(UVICORN) app.main:app --reload --port 8000

ui:
	streamlit run streamlit/App.py

seed:
	$(PY) scripts/seed_labels.py

watcher:
	$(PY) -m app.services.watcher

flows:
	$(PY) scripts/build_flows.py

watcher-ws:
	$(PY) -m app.services.watcher --mode ws --interval 0.5

watcher-poll:
	$(PY) -m app.services.watcher --mode poll

scan:
	$(PY) scripts/scan_contract_calls.py --range 10
