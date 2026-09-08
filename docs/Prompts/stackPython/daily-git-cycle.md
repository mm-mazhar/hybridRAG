# Daily git commit, push, and pull cycle

You never work on `main`. A normal day is: sync `main` → branch → commit locally → push the branch → open/update a PR → merge → pull `main`.

Canonical rules: `[.agents/rules/git.md](../../.agents/rules/git.md)`. Hooks: `lefthook.yml` (`post-checkout`, `pre-commit`, `commit-msg`, `pre-push`).

First clone on a new machine:

```bash
uv sync
uv run lefthook install
```

Or `make setup`.

## Start of day (or before new work)

```bash
git checkout main
git pull origin main
git checkout -b feat/short-description
```

The checkout hook accepts `feat/`, `fix/`, `bugfix/`, `refactor/`, `docs/`, `style/`, `test/`, `chore/`, `ci/`, `perf/`, `build/`, `revert/`. It rejects names like `my-work`.

## While coding

```bash
git add path/to/file.py          # specific files only, never git add -A
git commit -m "feat(app): add sitemap timeout"
```

On commit, lefthook:

- runs ruff fix/format on staged `*.py` and restages fixes
- runs mypy
- checks the message: `<type>(optional-scope): lowercase subject` (no trailing period, ≤100 chars)

If you are still on `main`, create the branch first. Do not `--no-verify`. Never commit `.env` or secrets.

## Push / share

```bash
git push -u origin HEAD          # first time
git push                         # later
```

`pre-push` runs `pytest`. After the first push, open a PR. Later pushes update that PR.

- **PR title** uses the same format as commits (`feat(scope): subject`). Squash-merge uses that title as the commit on `main`.
- Keep the PR **draft** until you want review. Copilot only reviews non-draft PRs.
- Wait for required checks **Lint**, **Types**, and **Tests** to go green, then squash-merge on GitHub. Do not merge-commit or rebase-merge.

Do not `git push origin main`. After merge, CI also runs on `main` as confirmation.

## Stay current with `main`

```bash
git fetch origin
git merge origin/main            # or rebase onto origin/main
git push
```

## After the PR merges

```bash
git checkout main
git pull origin main
git branch -d feat/short-description
```

Then start the next branch from the updated `main`.

## What you do not do daily

- commit or push to `main` (you may `checkout`/`pull` it; GitHub rejects `push`)
- force-push `main` or other shared branches
- merge-commit or rebase-merge a PR (squash only)
- commit `.env` / secrets
- skip hooks (`--no-verify`)
- tag a release (`v*`) unless you intend to publish

## When you actually want a PyPI release

1. On pypi.org → your account → Publishing → add a trusted publisher:
   1. Owner: `user-id`
   2. Repository: `<name>`
   3. Workflow: `release.yml`
   4. Environment: `pypi`
2. Then from `main`:
   - `git tag v0.1.0`
   - `git push origin v0.1.0`
   