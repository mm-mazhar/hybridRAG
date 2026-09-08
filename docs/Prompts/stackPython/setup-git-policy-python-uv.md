# Prompt — Set up git branch & commit policy for a Python project using uv

You are a senior Python engineer. Set up the git workflow policy (branch naming, commit
messages, local hooks, CI gates) in the current Python repository, which is managed with
**uv**. The conventions mirror the ChatbotX repo. Create/modify only the files listed
below, run the listed commands, and finish with the verification checklist. Report every
file you created or changed.

## 0. Assumptions

- Package layout: `src/<package>/` + `tests/`. If the repo uses a flat layout, adjust
  `mypy`/`pytest` paths accordingly (say so in your report).
- Default branch is `main`.
- Python version is pinned via `.python-version` (run `uv python pin 3.12` or the
  version the project already uses).

## 1. Add tooling as dev dependencies

```bash
uv add --dev ruff mypy pytest lefthook
```

Notes:
- `lefthook` is published on PyPI and wraps the native binary. If it is unavailable in
  your environment, install the lefthook binary another way (brew/scoop/go install) and
  still create `lefthook.yml`; document the manual `lefthook install` step in the README.
- Do NOT pin exact versions; let uv resolve and commit the updated `uv.lock`.

Ensure `pyproject.toml` contains lint/type/test config (add if missing):

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
files = ["src", "tests"]
check_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 2. Create `lefthook.yml` (repo root)

This is the single enforcement point: branch naming on `post-checkout`, lint/format +
typecheck on `pre-commit`, conventional commit message on `commit-msg`.

```yaml
post-checkout:
  jobs:
    - name: branch-name
      run: |
        BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)
        PATTERN='^(feat|fix|bugfix|refactor|docs|style|test|chore|ci|perf|build|revert)/.+'
        # Skip checks for detached HEAD, main, master, develop, release, and bot branches
        if echo "$BRANCH" | grep -qE '^(main|master|develop|HEAD|release/.+|dependabot/.+|renovate/.+)$'; then
          exit 0
        fi
        if ! echo "$BRANCH" | grep -qE "$PATTERN"; then
          echo "Invalid branch name: '$BRANCH'"
          echo ""
          echo "Expected: <type>/<description>"
          echo "  Types: feat, fix, bugfix, refactor, docs, style, test, chore, ci, perf, build, revert"
          echo "  Example: feat/export-csv"
          echo "  Example: fix/timeout-on-retry"
          echo ""
          echo "Rename it with: git branch -m <new-name>"
          exit 1
        fi

pre-commit:
  jobs:
    - run: uv run ruff check --fix {staged_files}
      glob: "*.py"
      stage_fixed: true
    - run: uv run ruff format {staged_files}
      glob: "*.py"
      stage_fixed: true
    - name: typecheck
      run: uv run mypy
      glob: "**/*.py"

commit-msg:
  jobs:
    - run: |
        MSG=$(cat {1})
        PATTERN='^(feat|fix|bugfix|refactor|docs|style|test|chore|ci|perf|build|revert)(\(.+\))?!?: .{1,100}$'
        if ! echo "$MSG" | grep -qE "$PATTERN"; then
          echo "Invalid commit message format."
          echo ""
          echo "Expected: <type>(<scope>): <subject>"
          echo "  Types: feat, fix, bugfix, refactor, docs, style, test, chore, ci, perf, build, revert"
          echo "  Append ! before the colon to mark a breaking change: feat(api)!: drop v1 endpoints"
          echo "  Example: feat(api): add pagination to list endpoint"
          echo ""
          echo "Got: $MSG"
          exit 1
        fi

# Optional but recommended: run tests before pushing instead of on every commit.
pre-push:
  jobs:
    - run: uv run pytest -q
```

Install the hooks into `.git/hooks`:

```bash
uv run lefthook install
```

Make sure every contributor gets hooks after clone: if `lefthook`'s installer doesn't
already run automatically, add a `postinstall`-equivalent (e.g. a `make setup` /
`just setup` target, or README instruction: `uv sync && uv run lefthook install`).
## 3. Create `.agents/rules/git.md` (canonical human-readable rules)

```markdown
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
```

## 4. Create `.github/workflows/ci.yml`

Three independent jobs on every PR and on push to `main`. Types/Tests/Lint each get
their own runner. Note: `uv sync --locked` fails CI if `uv.lock` is out of date — keep it.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - name: Install uv
        uses: astral-sh/setup-uv@v6   # pin the latest major at setup time
        with:
          enable-cache: true
      - run: uv sync --locked
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    name: Types
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - run: uv sync --locked
      - run: uv run mypy

  test:
    name: Tests
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - run: uv sync --locked
      - run: uv run pytest -q
```

## 5. Create `.github/workflows/pr-labeler.yml`

Copy the ChatbotX approach: on `pull_request_target (opened, edited, reopened)`, a
`actions/github-script` job maps the conventional-commit prefix in the PR title to
labels (`feature`, `bug`, `breaking-change`, `improvement`, `docs`, `chore`, `ci`,
`security`, `dependencies`). Reuse the exact `TYPE_MAP` regex list from ChatbotX's
`.github/workflows/pr-labeler.yml`. Labels must be bootstrapped once in the repo
settings; the workflow only applies them.

## 6. Create `.github/dependabot.yml`

```yaml
version: 2
updates:
  # Dependabot supports uv via the pip ecosystem (reads uv.lock / pyproject.toml).
  # If your GitHub plan doesn't pick up uv.lock, switch this repo to Renovate with
  # the uv manager instead — do not silently drop dependency updates.
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    groups:
      dev-dependencies:
        dependency-type: "development"
    commit-message:
      prefix: "chore(deps)"
      prefix-development: "chore(deps-dev)"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(ci)"
```

The `chore(deps)` / `chore(ci)` prefixes keep bot PR titles compatible with the
conventional-commit PR title convention.

## 7. Optional: release workflow (PyPI on `v*` tags)

Create `.github/workflows/release.yml`:

```yaml
name: Release to PyPI

on:
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write   # Trusted Publishing (OIDC)
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - run: uv sync --locked
      - run: uv run pytest -q
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

Also create `.github/release.yml` with category labels (breaking-change, feature, bug,
improvement, chore/ci/docs/dependencies) and a `CHANGELOG.md` skeleton (Keep a
Changelog format).

## 8. Protect `main` the ChatbotX way — EXECUTE, do not only document

ChatbotX does **not** use classic Settings → Branches → Branch protection.
It uses **repository rulesets**. Last time we only wrote a README note; `main`
stayed unprotected. **Create the rulesets in this step.**

### ChatbotX `main` ideology (language-agnostic — copy the flow)

`main` is a merge target, not a working branch.

1. **Nothing lands on `main` except through a PR.** Direct push is blocked.
2. **PRs squash-merge only.** History on `main` is one commit per PR, titled
   like a conventional commit (`feat(scope): subject`).
3. **`main` cannot be deleted or force-pushed** (`deletion` + `non_fast_forward`).
4. **CI is a gate on the PR, then a confirmation on `main`.**
   Workflow `on: pull_request` plus `on: push: branches: [main]`.
   After this policy PR merges, the next push to `main` is the first time
   Lint / Types / Tests appear on the default branch. Until `ci.yml` is on
   `main`, that branch has no new checks — do not treat that as "skip
   protection."
5. **Required reviews can be 0** so a solo maintainer can merge their own PR.
   ChatbotX sets `required_approving_review_count: 0` and
   `require_extra_approval_for_unattributed_changes: true`.
6. **Copilot reviews non-draft PRs to the default branch** (optional second
   ruleset). Not Python-specific; create it when the repo has Copilot.
   ChatbotX: `review_on_push: false`, `review_draft_pull_requests: false`.
7. **Do not commit to `main` locally.** Hooks allow the branch name `main`;
   GitHub rejects the push. Always `git checkout -b <type>/<description>`.

ChatbotX's live `protect_main` ruleset (id 14490247) is PR + squash + no
delete/force-push. It does **not** require CI status checks. This Python
prompt **does** require `Lint` / `Types` / `Tests` so a red PR cannot merge.
That is the one intentional overlay.

### 8a. Create `protect_main` (required)

Need `admin` on the repo. Payload: `docs/Prompts/protect_main.ruleset.json`
(same JSON as below).

```bash
gh api repos/OWNER/REPO/rulesets --method POST --input docs/Prompts/protect_main.ruleset.json
```

```json
{
  "name": "protect_main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": ["~DEFAULT_BRANCH", "refs/heads/main"]
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "require_extra_approval_for_unattributed_changes": true,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "Lint" },
          { "context": "Types" },
          { "context": "Tests" }
        ]
      }
    }
  ]
}
```

Verify: `gh api repos/OWNER/REPO/rulesets` shows `protect_main` with
`enforcement: active`. A direct `git push origin main` must be rejected.

### 8b. Copilot review ruleset (optional — ChatbotX has this)

```bash
gh api repos/OWNER/REPO/rulesets --method POST --input - <<'EOF'
{
  "name": "Copilot review for default branch",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": { "exclude": [], "include": ["~DEFAULT_BRANCH"] }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "copilot_code_review",
      "parameters": {
        "review_on_push": false,
        "review_draft_pull_requests": false
      }
    }
  ]
}
EOF
```

If the API rejects `copilot_code_review`, skip it and say so in the report.
Do not fail the whole setup.

### 8c. README note (still required)

Document that `main` is protected by the `protect_main` **ruleset** (not
classic branch protection): PRs only, squash merge, no delete/force-push,
required checks `Lint` / `Types` / `Tests`. Point at Settings → Rules.

## 9. Verification checklist (run all of these)

1. `uv run lefthook install` succeeds; `.git/hooks` contains lefthook-generated hooks.
2. `git checkout -b "bad_branch_name"` -> hook rejects it. `git branch -m feat/policy-setup` -> accepted.
3. `git commit --allow-empty -m "bad message"` -> commit-msg hook rejects it.
4. `git commit --allow-empty -m "feat: valid message"` -> passes.
5. Add an unformatted `*.py` file with an unused import, stage it, commit -> ruff fixes
   and the fix is restaged automatically (`stage_fixed: true`).
6. `uv run ruff check . && uv run mypy && uv run pytest -q` all pass locally.
7. `uv sync --locked` passes (lockfile committed and up to date).
8. Push the branch and open a draft PR to confirm the CI jobs turn green, then report.
9. `gh api repos/OWNER/REPO/rulesets` lists `protect_main` with `enforcement: active`.
10. Do **not** test by force-pushing `main`. Confirm in the GitHub UI (Settings → Rules)
    that PRs are required, squash-only, and `Lint` / `Types` / `Tests` are required.

## 10. Other misses to apply next time (not all Python-specific)

- **Windows leftover scripts.** Inline multiline `run: |` in `lefthook.yml` often
  dies under Git Bash `sh -c` (`syntax error: unexpected end of file`). Put
  branch-name and commit-msg bodies in `.lefthook/<hook>/*.sh` with `runner: bash`
  and LF line endings. Keep the same regexes.
- **Pin `astral-sh/setup-uv` to the latest full tag** (e.g. `v10.0.1`), not `@v6`.
  From v8 onward moving major tags may not resolve. Comment in the prompt said
  "latest major at setup time" — look it up.
- **Keep the repo's existing `.python-version`.** Do not pin 3.12 if the project
  is already 3.13 (or any other version). Align `requires-python`,
  `tool.ruff.target-version`, and `tool.mypy.python_version`.
- **`main` has no new CI until `ci.yml` is merged.** The workflow file on the
  feature branch does not run for the default branch. Protection + required
  checks still belong in this setup, not after "we see checks on main."
- **Do not use classic branch protection** if you are copying ChatbotX. Use
  rulesets (`protect_main`). Classic Settings → Branches is a different product.
