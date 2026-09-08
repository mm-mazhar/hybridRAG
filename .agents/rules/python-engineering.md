---
description: Technical standards for Python web services, APIs, background jobs, and AI application architecture.
globs: "**/*.py, pyproject.toml, requirements*.txt, alembic.ini, alembic/**/*.py"
---

# Python Engineering Standards

<Philosophy>
We build "Schema-First". API contracts, validation models, and persistence boundaries are the source of truth.
We separate request validation, business logic, and transport concerns.
We prefer explicit typing, validation, and service boundaries over framework magic.
</Philosophy>

## 1. API & Data Layer (Strict Requirement)
**Trigger Skills or Powers:** Use `/pydantic` for schema-first validation design at `/skills/pydantic/skill.md` or `/power/intalled/pydantic/power.md`, `/fastapi-python` for FastAPI handler and async API patterns at `/skills/fastapi-python/skill.md` or `/power/intalled/fastapi-python/power.md`, and `/python-type-safety` when tightening public type contracts at `/skills/python-type-safety/skill.md` or `/power/intalled/python-type-safety/power.md`.

**The Golden Rule:** Do not mix route handlers, database queries, and business rules in a single function. Use validated schemas and a service layer.

### Workflow: Schema-First Development
Before building handlers, establish the contract:
1. **Define Schema:** Create request and response models using `pydantic`
2. **Define Service:** Implement domain logic in a service/module layer, separate from transport.
3. **Register Route/Task:** Wire the service into FastAPI, Flask, Django, or worker entrypoints.
4. **Implement Consumers:** Only then build UI integrations, jobs, or downstream clients.

### Implementation Patterns
* **FastAPI / API Handlers:**
  Keep handlers thin. Validate input at the edge and delegate to services.

  ```python
  from fastapi import APIRouter, Depends
  from pydantic import BaseModel

  router = APIRouter()

  class ProjectCreate(BaseModel):
      name: str

  @router.post("/projects")
  async def create_project(payload: ProjectCreate, service=Depends(...)):
      return await service.create_project(payload)
  ```

* **Background Jobs / Workers:**
  Reuse the same service layer instead of duplicating business logic inside Celery, RQ, or cron tasks.

## 2. Folder Organization (Suggestion)

**Recommended structure** - adapt to project needs:
* **Package Manager:** Detect `pyproject.toml`, `poetry.lock`, `uv.lock`, `requirements.txt`, or `Pipfile.lock`. Always use the detected toolchain consistently.

```text
app/
├── api/                  # Route handlers / routers
├── schemas/              # Pydantic models / DTOs
├── services/             # Business logic
├── repositories/         # Data access boundaries
├── db/                   # Session, models, migrations helpers
├── auth/                 # AuthN/AuthZ logic
├── ai/                   # AI logic, retrieval, prompts, tools
├── tasks/                # Background jobs / schedulers
├── core/                 # Config, logging, shared utilities
tests/
├── unit/
├── integration/
└── e2e/
```

**Check for:**
- Business logic embedded directly in route handlers
- Database calls mixed into presentation or worker entrypoints
- AI logic outside `/ai` when there is a retrieval or agent layer
- Duplicate validation logic across handlers and services

## 3. Database & Data Access

* Role of the database layer: persistence only. Avoid leaking ORM objects across unrelated boundaries unless the project explicitly standardizes that pattern.
* **Access Pattern:**
  * **Allowed:** repositories, services, dedicated data modules.
  * **Forbidden:** raw SQL or direct model mutations scattered across handlers without validation or authorization checks.
* **Read Pattern:** validate filters, scope by tenant/user, and return typed response models where possible.
* **Write Pattern:** enforce authorization, transaction boundaries, and audit-sensitive updates.

## 4. Security & Validation
**Trigger Skills or Powers:** Use `/security-patterns` for input validation, authorization, secret handling, OWASP risks, prompt-injection defense, and LLM safety review at `/skills/security-patterns/skill.md` or `/power/intalled/security-patterns/power.md`. This replaces the non-installed `/api-security-best-practices` and `/security-reviewer` references in this file.

* **Input Validation:** All external inputs must be validated with schemas or explicit parsing.
* **Authorization:** Enforce object-level and tenant-level checks in services, not only at the router layer.
* **Secrets:** Never hardcode credentials, tokens, signing keys, or API secrets.
* **Rate Limiting:** Add rate limiting where public or abuse-prone endpoints exist.
* **Vector DB & Retrieval:** Validate filters, isolate tenant namespaces, defend against prompt injection in retrieved content, and avoid leaking sensitive documents through semantic search.

## 5. Async & Runtime Patterns

Rule: use async only when the stack supports it end-to-end and dependencies are async-safe.

```python
async def get_project(project_id: str, service) -> dict:
    project = await service.get_project(project_id)
    return {"id": project.id, "name": project.name}
```

* Do not block the event loop with sync I/O inside async handlers.
* Use task queues for long-running or retry-heavy work.

## 6. UI / Template Standards

* Keep templates or presentation layers thin.
* Components, pages, or templates should compose validated data rather than contain business logic.
* If the project has a frontend boundary, keep API contracts explicit and versionable.

## 7. AI Feature Implementation
* **Provider Agnostic:** Do not hardcode one LLM provider unless explicitly requested.
* **Context:** Ask the user for provider/model preference before scaffolding AI features.
* **Retrieval:** Expose retrieval and generation through typed service boundaries, not ad hoc scripts.

## Notes
* **Context Awareness:** Search existing services, schemas, and tests before introducing new patterns.
* **Refactoring:** If you see route handlers doing validation, authorization, and persistence inline, flag it and propose extraction into services.
