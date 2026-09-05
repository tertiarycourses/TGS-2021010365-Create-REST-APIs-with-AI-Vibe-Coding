# Lab 05 Prompts: Validate Product and Customer Data

**Course:** Create RESTful APIs and Web Apps with Python Flask
**Course code:** TGS-2021010365
**Version:** v11.0
**Maps to:** A3, A5

## Prompt execution contract

Use `python ai_vibe.py --dry-run` to inspect the exact request. The script uses the OpenAI Python SDK Responses API with a Pydantic `CodeBundle`. It writes drafts only to `working-files/generated/`; it never overwrites trusted source. Keep `OPENAI_API_KEY` in the shell, not in prompts, files, screenshots or browser JavaScript.

## Learner prompt - copy exactly for the first run

You are working on Lab 05 of a Northstar Commerce API. Create Pydantic v2 Product, Customer, Order and OrderItem input/output models. Constrain SKU, email, Decimal price, stock quantity and status; distinguish required, optional and omitted values. Add schema examples and boundary tests that assert the exact 422 error locations for invalid mock requests.

Use only the synthetic context in `mock-data.json` and the current project files supplied by `ai_vibe.py`. Preserve existing API behaviour unless this prompt explicitly changes it. Use Python 3.11+, FastAPI, Pydantic v2, SQLite parameter binding and pytest/TestClient. Do not include secrets, database files, caches or invented test results. Return a typed `CodeBundle` containing complete file contents for only these targets:

- `app/schemas.py`
- `tests/test_validation.py`

For every generated file, state its purpose. Include assumptions and concrete verification commands. The learner will review the diff and run the commands before accepting any code.

## Evidence-led refinement prompt

The previous generated bundle did not yet pass the acceptance check below. Use the pasted failure evidence, identify the smallest contract or implementation mismatch, and return a revised `CodeBundle` containing only files that must change. Do not weaken or delete a passing test.

**Acceptance check:** Invalid SKU, price, stock, email and status values are rejected before repository code; valid JSON becomes a typed model.

**Paste exact evidence here:**

```text
HTTP request/response, traceback, assertion diff or log request ID
```

## Review checklist

- Confirm every generated path is inside `working-files/generated/`.
- Reject hard-coded keys, personal data, f-string SQL and unrestricted CORS.
- Compare generated behaviour with the written API contract and mock data.
- Run `pytest -q`; inspect status, JSON and SQLite state, not only the exit code.
- Record prompt, model name, assumptions, accepted diff and final evidence.
