---
description: Standards for unit, integration, and end-to-end testing in Python projects.
globs: "**/test_*.py, **/*_test.py, **/tests/**/*.py"
---

# Testing Standards

## 1. E2E & Browser Automation
**Trigger Skill or Powers:** Use `/pytest` for test execution, fixtures, async tests, and framework integration at `/skills/pytest/skill.md` or `/power/intalled/pytest/power.md`, or use `/python-testing-patterns` for broader test suite design, mocking strategy, and testing architecture at `/skills/python-testing-patterns/skill.md` or `/power/intalled/python-testing-patterns/power.md`.

* **Tool:** Playwright for browser flows when the project has a web UI.
* **Rule:** Do not hand-roll large browser automation setups if an existing testing workflow or skill can scaffold them.
* **Scope:** User flows, authentication, payment handling, critical UI paths, and major regressions.

## 2. Unit & Integration Testing
* **Tool:** `pytest`
* **Scope:** Business logic, services, utility functions, API handlers, and retrieval pipelines.
* **Structure:**
  * Use clear arrange/act/assert sections.
  * Keep each test focused on one behavior.
  * Prefer fixtures for shared setup.
  * Mock external dependencies only at the system boundary.

## 3. Mocking Strategy
* **Database:** Prefer integration tests against a test database when behavior depends on ORM/query semantics.
* **External APIs:** Mock all outbound HTTP calls, LLM providers, vector DB providers, and payment/webhook integrations.
* **Files and Storage:** Use temp directories or isolated test buckets instead of live services.

## 4. AI & Vector Retrieval Testing
* Test prompt-building and retrieval pipelines for tenant isolation and sensitive-data leakage.
* Verify metadata filters, namespace scoping, and fallback behavior when retrieval returns unsafe or irrelevant content.
