# Lab 01 Prompts: Prompt a REST API Contract

**Course:** Create RESTful APIs and Web Apps with Python Flask
**Course code:** TGS-2021010365
**Version:** v11.0
**Maps to:** A1, A2

## Prompt execution contract

Use `python ai_vibe.py --dry-run` to inspect the exact request. The script uses the OpenAI Python SDK Responses API with a Pydantic `CodeBundle`. It writes drafts only to `working-files/generated/`; it never overwrites trusted source. Keep `OPENAI_API_KEY` in the shell, not in prompts, files, screenshots or browser JavaScript.

## Learner prompt - copy exactly for the first run

You are working on Lab 01 of a Northstar Commerce API. Create a behaviour-first OpenAPI 3.1 contract for Northstar Commerce using FastAPI and SQLite. Define Product, Customer, Order and OrderItem schemas; list collection/member routes, request and response JSON, 200/201/204/401/404/409/422 outcomes, and at least six acceptance tests. Do not write implementation code yet. Return only api-contract.md, openapi-draft.yaml and machine-readable test cases.

Use only the synthetic context in `mock-data.json` and the current project files supplied by `ai_vibe.py`. Preserve existing API behaviour unless this prompt explicitly changes it. Use Python 3.11+, FastAPI, Pydantic v2, SQLite parameter binding and pytest/TestClient. Do not include secrets, database files, caches or invented test results. Return a typed `CodeBundle` containing complete file contents for only these targets:

- `api-contract.md`
- `tests/contract-cases.json`

For every generated file, state its purpose. Include assumptions and concrete verification commands. The learner will review the diff and run the commands before accepting any code.

## Evidence-led refinement prompt

The previous generated bundle did not yet pass the acceptance check below. Use the pasted failure evidence, identify the smallest contract or implementation mismatch, and return a revised `CodeBundle` containing only files that must change. Do not weaken or delete a passing test.

**Acceptance check:** The contract covers products, customers and orders, names 200/201/204/401/404/409/422 outcomes and validates as OpenAPI 3.1.

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
