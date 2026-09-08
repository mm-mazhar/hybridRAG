---
description: Standard operating procedure for Python development cycles.
globs: "**/*"
---

# Development Lifecycle & Skill Triggers

Follow this sequence for every feature request or project initiation.

## Phase 0: Environment & Context (Critical)
**Goal:** Align with the existing Python environment to prevent drift.

1. **Package Manager Detection**
   * **Action:** Check for `uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.txt`, or `pyproject.toml`.
   * **Rule:** Strictly use the detected package manager and task runner for install/run commands.
       * if `uv` -> `uv sync`, `uv run`
       * if `poetry` -> `poetry install`, `poetry run`
       * if plain `pip` -> project-approved virtualenv + `pip install -r requirements.txt`
   * **Do not mix** package managers without an explicit reason.

2. **Planning Mode Check**
   * **Condition:** Check if the environment has native planning support.
   * **Fallback Trigger Skill or Powers:** Use `/pi-planning-with-files` if native planning is absent at `/skills/pi-planning-with-files/skill.md` or `/power/intalled/pi-planning-with-files/power.md`.

## Phase 1: Planning & Architecture
**Goal:** Define what we are building before writing code.

3. **Requirement Analysis & Task Tracking**
   * **Condition:** Check if the current environment has a built-in planning mode.
   * **Primary Action:** Use the environment's native planner to define phases.
   * **Fallback Trigger Skill or Powers:** Use `/pi-planning-with-files` at `/skills/pi-planning-with-files/skill.md` or `/power/intalled/pi-planning-with-files/power.md`.
   * **Universal Rule:** Do not start coding without a defined plan.
   * **AI Feature Check:** If building AI features, ask the user which LLM provider/model to target.

4. **System Design**
   * **Action:** Define API boundaries, schema models, services, data access, background jobs, and auth flow before implementation.
   * **Constraint:** Reuse existing project conventions before introducing a new framework or abstraction.

## Phase 2: Core Implementation
**Goal:** Implement logic, data access, auth, and interactivity in the right layers.

5. **Handler and Service Design**
   * **Action:** Keep route handlers, commands, and jobs thin.
   * **Rule:** Put business logic in services/modules, not directly in controllers or views.

6. **Data Architecture**
   * **Action:** Design schema -> migration -> repository/service access -> tests.
   * **Rule:** Validate inputs before persistence and enforce tenant/user scoping in reads and writes.

7. **Authentication & Security**
   * **Trigger Skills or Powers:** Use `/security-patterns` at `/skills/security-patterns/skill.md` or `/power/intalled/security-patterns/power.md`.
   * **Action:** Implement authentication, authorization, secret handling, and input validation early.
   * **Rule:** Do not rely only on UI gating; enforce permissions server-side.

8. **AI / Vector DB Logic (If applicable)**
   * **Action:** Define retrieval boundaries, document ingestion rules, metadata filters, and tenant isolation.
   * **Rule:** Review prompt injection, poisoned content, and semantic search leakage risks before shipping.

## Phase 3: Verification & Polish
**Goal:** Ensure quality before shipping.

9. **Functional Testing**
   * **Action:** Use `pytest` for unit/integration tests and Playwright for browser flows when applicable.
   * **Rule:** Cover core business logic, auth boundaries, and data access behavior.

10. **Security Audit**
    * **Trigger Skill or Powers:** Use `/security-patterns` at `/skills/security-patterns/skill.md` or `/power/intalled/security-patterns/power.md`.
    * **Action:** Audit authz/authn, ORM/query safety, file handling, secrets, dependencies, and vector DB isolation.

11. **Operational Readiness**
    * **Action:** Verify configuration, environment variables, logging, migrations, and deployment assumptions.
    * **Rule:** Do not ship debug settings, verbose secrets, or unbounded retries to production.
