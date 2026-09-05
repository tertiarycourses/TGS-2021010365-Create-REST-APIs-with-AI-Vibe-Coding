# Lab 12 Prompts: Document and Bundle the Capstone

**Course:** Create RESTful APIs and Web Apps with Python Flask
**Course code:** TGS-2021010365
**Version:** v11.0
**Maps to:** A4, A6, A8

## Prompt execution contract

Use `python ai_vibe.py --dry-run` to inspect the exact request. The script uses the OpenAI Python SDK Responses API with a Pydantic `CodeBundle`. It writes drafts only to `working-files/generated/`; it never overwrites trusted source. Keep `OPENAI_API_KEY` in the shell, not in prompts, files, screenshots or browser JavaScript.

## Learner prompt - copy exactly for the first run

You are working on Lab 12 of a Northstar Commerce API. Review the complete FastAPI/SQLite/browser project and generate release documentation only. Include clean setup, test, run and verification commands; OpenAPI and environment notes; a bundle inventory; and a checklist excluding .env, databases, caches and virtual environments. Do not invent passing evidence.

Use only the synthetic context in `mock-data.json` and the current project files supplied by `ai_vibe.py`. Preserve existing API behaviour unless this prompt explicitly changes it. Use Python 3.11+, FastAPI, Pydantic v2, SQLite parameter binding and pytest/TestClient. Do not include secrets, database files, caches or invented test results. Return a typed `CodeBundle` containing complete file contents for only these targets:

- `README.md`
- `environment.template`
- `release-checklist.md`

For every generated file, state its purpose. Include assumptions and concrete verification commands. The learner will review the diff and run the commands before accepting any code.

## Evidence-led refinement prompt

The previous generated bundle did not yet pass the acceptance check below. Use the pasted failure evidence, identify the smallest contract or implementation mismatch, and return a revised `CodeBundle` containing only files that must change. Do not weaken or delete a passing test.

**Acceptance check:** A clean copy installs, tests, starts, serves the storefront/CRM dashboard, completes catalog/customer/order flows and contains no secret or database file.

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
