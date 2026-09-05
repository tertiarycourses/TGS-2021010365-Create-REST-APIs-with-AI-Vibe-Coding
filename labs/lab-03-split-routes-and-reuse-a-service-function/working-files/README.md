# Northstar Commerce FastAPI Demo

This realistic classroom app combines an e-commerce catalog, a small CRM, order processing and live dashboard metrics:

`HTML/CSS/JavaScript -> fetch() -> FastAPI -> Pydantic -> parameterized SQLite transactions`

The numbered labs add a controlled vibe-coding workflow:

`Prompts.pdf -> ai_vibe.py -> OpenAI Responses API -> typed CodeBundle -> generated/ -> review + pytest`

## VS Code setup

Install Visual Studio Code, then add these extensions from the Extensions view:

- Python (Microsoft)
- Pylance (Microsoft)
- REST Client (Huachao Mao)
- SQLite Viewer (Florian Klampfer)
- YAML (Red Hat)

Open the folder in VS Code and use `Python: Select Interpreter` to select `.venv`.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export APP_API_KEY=course-demo-key
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/> for the responsive commerce dashboard and <http://127.0.0.1:8000/docs> for Swagger UI.

## Test

```bash
pytest -q
```

JavaScript never opens SQLite directly. The browser calls the versioned FastAPI contract, FastAPI validates the request, and parameterized SQL performs the database work. Order creation uses one transaction so insufficient stock rolls back the entire change.
