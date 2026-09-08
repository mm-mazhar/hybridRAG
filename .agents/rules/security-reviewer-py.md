---
description: Trigger specific security auditing and review workflows for Python-based projects.
globs: "**/*"
---

# Security Review Protocol

**Trigger:** When the user asks to "review security", "audit code", "check for vulnerabilities", or "security check" for a Python-based project.

## Action
Invoke **/security-patterns** at `/skills/security-patterns/skill.md` or `/power/intalled/security-patterns/power.md`.

## Scope
The security reviewer should focus on:
1. **OWASP Top 10** vulnerabilities (Injection, Broken Auth, SSRF, IDOR, etc.).
2. **Python/Web Framework Specifics**: Unsafe deserialization, insecure file handling, path traversal, template injection, subprocess command injection, and missing input validation in Django, Flask, FastAPI, or similar frameworks.
3. **Authentication and Authorization**: Session handling, JWT validation, RBAC/ABAC gaps, privilege escalation, and missing object-level access checks.
4. **Database and ORM Usage**: Raw SQL misuse, unsafe query construction, migration risks, insecure defaults, and excessive database privileges.
5. **Vector DB and LLM Retrieval Security**: Prompt injection through retrieved content, tenant data leakage across namespaces, insecure metadata filtering, poisoned embeddings/documents, unvalidated retrieval pipelines, and exposure of sensitive data in semantic search results.
6. **Secrets Management**: Checking for hardcoded keys, tokens, credentials, and unsafe environment variable handling.
7. **Dependency and Runtime Risks**: Vulnerable packages, insecure default configuration, debug mode exposure, weak CORS/CSRF protections, and missing rate limiting.

## Output
Provide a structured report prioritizing:
* **Critical**: Immediate vulnerabilities (e.g., SQL injection, auth bypass, tenant data leakage in vector search).
* **High**: Missing validation, unsafe deserialization, IDOR, insecure retrieval filters, or privilege escalation paths.
* **Moderate**: Configuration best practices (headers, logging hygiene, rate limiting, dependency hardening).
