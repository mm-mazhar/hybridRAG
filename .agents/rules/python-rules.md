---
paths: "**/*.py"
---

## Python Rules

### Naming Conventions
- PascalCase for classes
- snake_case for functions, variables, methods, and modules
- UPPER_SNAKE_CASE for constants
- Prefer descriptive package and file names

### Type Safety
- Use type hints on exported/public functions
- Avoid `Any` without explicit justification
- Prefer precise built-in and `typing` types over vague annotations
- Use `TypedDict`, `Protocol`, `Literal`, or `pydantic` models when they clarify contracts

### Imports
- Group imports: standard library -> third-party -> internal
- Prefer explicit imports over wildcard imports
- No circular dependencies

### Async/Await
- Always handle async errors explicitly
- Use `await` consistently; avoid fire-and-forget tasks unless intentionally managed
- Do not mix sync and async database/client calls carelessly

### Framework Best Practices
- Keep framework handlers thin and move domain logic into services
- Validate external inputs at the boundary
- Favor pure functions and testable modules where possible

### State and Derived Values
- Prefer derived values over mutable shared state
- Use caching or memoization only when there is a measurable need
