# Git Conventions

## Commit Message Format

Enforced by `lefthook.yml` commit-msg hook. Pattern:

```
<type>(<scope>): <subject>
```

**Types:** `feat`, `fix`, `bugfix`, `refactor`, `docs`, `style`, `test`, `chore`, `ci`, `perf`, `build`, `revert`

Examples:
```
feat(auth): add OAuth2 login
fix: handle null response from API
chore(deps): bump httpx to 0.28
```

- Subject must be <= 100 characters
- Lowercase after the colon, no trailing period
- Append `!` before the colon for breaking changes: `feat(api)!: ...`

## Branch Naming

```
feat/<issue-or-description>
fix/<issue-or-description>
bugfix/<issue-or-description>
chore/<description>
refactor/<description>
```

Enforced by the `post-checkout` hook. Exempt: `main`, `master`, `develop`, detached
`HEAD`, `release/*`, `dependabot/*`, `renovate/*`.

## Working Branch

- **Never commit directly to `main`/`master`.** They only advance through merged PRs.
- If on `main` when about to commit, create a feature branch first:
  `git checkout -b <type>/<description>`.
- Never force-push shared branches.

## Staging Rules

- **Never** `git add -A` or `git add .` — stage specific files only
- **Never** commit `.env` files or secrets
- **Never** skip hooks (`--no-verify`)

## Pull Requests

- One feature or fix per PR; keep them small
- PR title uses the same format as commit messages (applied manually — not hook-enforced)
- Reference the issue number in title or body (e.g. `#42`)
- Run `uv run ruff check .`, `uv run mypy`, and `uv run pytest` before opening a PR

## After Merging

When a release is tagged, update `CHANGELOG.md` following
[Keep a Changelog](https://keepachangelog.com).
