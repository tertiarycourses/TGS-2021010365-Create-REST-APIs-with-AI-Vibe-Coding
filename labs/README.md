# Northstar Commerce Labs

These 12 self-contained labs build one coherent e-commerce and CRM application from contract design through a tested FastAPI/OpenAPI/SQLite release.

| Lab | Build progression | Primary evidence |
|---|---|---|
| [01](lab-01-prompt-a-rest-api-contract/) | OpenAPI-first product/customer/order contract | Valid contract and prompt critique |
| [02](lab-02-run-the-first-fastapi-service/) | First typed FastAPI routes | 200 and structured 422 responses |
| [03](lab-03-split-routes-and-reuse-a-service-function/) | Router/service separation | Stable OpenAPI route inventory |
| [04](lab-04-add-api-key-protection-and-cors/) | API-key dependency and CORS | Authorized and rejected requests |
| [05](lab-05-validate-product-and-customer-data/) | Product and CRM validation | Pydantic boundary failures |
| [06](lab-06-filter-responses-and-implement-patch/) | Output filtering and partial update | Stable response model and PATCH test |
| [07](lab-07-standardise-errors-and-request-logs/) | Error envelope and request trace | Response-to-log correlation |
| [08](lab-08-test-and-debug-the-api/) | Regression suite and VS Code debugging | Failing-then-passing test evidence |
| [09](lab-09-design-the-commerce-crm-database/) | Relational SQLite schema | Keys, checks and relationship proof |
| [10](lab-10-implement-sqlite-crud-and-orders-safely/) | CRUD and atomic order transaction | Rollback and stock evidence |
| [11](lab-11-connect-the-commerce-web-app/) | Responsive browser dashboard | Browser -> FastAPI -> SQLite trace |
| [12](lab-12-document-and-bundle-the-capstone/) | OpenAPI review and clean release | Test, start and secret-scan evidence |

Every lab folder includes `README.md`/PDF, `CHECKLIST.md`/PDF, `Prompts.md`/PDF, `ai_vibe.py`, synthetic `mock-data.json`, a detailed Lab Guide DOCX/PDF and a complete `working-files/` copy. The Python generation runner writes AI drafts only under `working-files/generated/` for review.

The reusable demonstration project is in [demo-website](demo-website/).
