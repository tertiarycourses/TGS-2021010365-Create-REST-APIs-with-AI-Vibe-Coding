# Lab 02: Run the First FastAPI Service

**Maps to:** A1, A4

**Objective:** Create and verify a typed product endpoint and its generated OpenAPI documentation.

**Build:** main.py with /health and /api/v1/products routes

**Tools:** Python, FastAPI, Uvicorn, Swagger UI, OpenAI Python SDK

## Lab asset inventory

- `ai_vibe.py` - OpenAI Python SDK runner with Pydantic structured output and safe generated-file paths
- `mock-data.json` - authorised synthetic scenario, route contract and test cases
- `mock-database.sqlite` - inspectable SQLite database seeded only with synthetic commerce and CRM records
- `Prompts.pdf` - learner-facing first-run, refinement and review prompts
- `Prompts.md` - copyable source used by the SDK runner
- `working-files/` - complete FastAPI, SQLite, HTML/CSS/JavaScript project, including VS Code REST Client requests

## AI vibe-coding control loop

`Prompts.pdf → ai_vibe.py → Responses API → CodeBundle → working-files/generated/ → pytest + human review`

## Detailed procedure

### Step 1 — Read Prompts.pdf and identify the role, context, constraints, target files and verification checks.

1. Perform the action exactly as stated: **Read Prompts.pdf and identify the role, context, constraints, target files and verification checks.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 2 — Inspect mock-data.json; remove any personal, confidential or live credential data before prompting.

1. Perform the action exactly as stated: **Inspect mock-data.json; remove any personal, confidential or live credential data before prompting.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 3 — Run python ai_vibe.py --dry-run to validate and preview the exact SDK request without using API credits.

1. Perform the action exactly as stated: **Run python ai_vibe.py --dry-run to validate and preview the exact SDK request without using API credits.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 4 — Set OPENAI_API_KEY in the shell and choose an available OPENAI_MODEL; never paste either value into source files.

1. Perform the action exactly as stated: **Set OPENAI_API_KEY in the shell and choose an available OPENAI_MODEL; never paste either value into source files.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 5 — Run python ai_vibe.py and inspect the typed CodeBundle written under working-files/generated/.

1. Perform the action exactly as stated: **Run python ai_vibe.py and inspect the typed CodeBundle written under working-files/generated/.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 6 — Review the generated diff and copy only accepted changes into the working application.

1. Perform the action exactly as stated: **Review the generated diff and copy only accepted changes into the working application.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 7 — Create and activate a virtual environment.

1. Perform the action exactly as stated: **Create and activate a virtual environment.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 8 — Install the packages from requirements.txt.

1. Perform the action exactly as stated: **Install the packages from requirements.txt.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 9 — Use the VS Code Python: Select Interpreter command to choose .venv.

1. Perform the action exactly as stated: **Use the VS Code Python: Select Interpreter command to choose .venv.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 10 — Open app/main.py and inspect the FastAPI application metadata.

1. Perform the action exactly as stated: **Open app/main.py and inspect the FastAPI application metadata.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 11 — Run uvicorn app.main:app --reload from the working-files folder.

1. Perform the action exactly as stated: **Run uvicorn app.main:app --reload from the working-files folder.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 12 — Open /docs and execute GET /health/live.

1. Perform the action exactly as stated: **Open /docs and execute GET /health/live.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 13 — Add GET /api/v1/products/{product_id} with product_id typed as int.

1. Perform the action exactly as stated: **Add GET /api/v1/products/{product_id} with product_id typed as int.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 14 — Send a non-integer ID and capture the 422 response as evidence.

1. Perform the action exactly as stated: **Send a non-integer ID and capture the 422 response as evidence.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 15 — Run pytest -q and the lab acceptance checks; refine the prompt with the observed failure evidence when needed.

1. Perform the action exactly as stated: **Run pytest -q and the lab acceptance checks; refine the prompt with the observed failure evidence when needed.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

### Step 16 — Save the prompt, model name, generated bundle summary and test result as the lab evidence trail.

1. Perform the action exactly as stated: **Save the prompt, model name, generated bundle summary and test result as the lab evidence trail.**
2. Observe the resulting file, HTTP response, log or browser state.
3. If the expected state is absent, compare the request contract, status code and latest log entry.
4. Save one evidence item before continuing.

## Acceptance criteria

- GET /health/live returns 200; /docs lists the product route; invalid path input returns structured 422 JSON.
- Evidence names the lab number and the mapped codes: A1, A4.
- The saved SDK evidence records the prompt, model, assumptions, generated file list and verification result.
- `mock-database.sqlite` contains synthetic seed data only; no `.env`, live credential, virtual environment or runtime `northstar.db` is submitted.

## Evidence checklist

- [ ] Prompts.pdf reviewed and dry run captured
- [ ] mock-data.json contains synthetic data only
- [ ] mock-database.sqlite opens in VS Code SQLite Viewer
- [ ] SDK CodeBundle saved under working-files/generated/
- [ ] Generated diff reviewed before applying
- [ ] Working artifact
- [ ] Request/response or test output
- [ ] One failure diagnosis
- [ ] Acceptance criterion confirmed
