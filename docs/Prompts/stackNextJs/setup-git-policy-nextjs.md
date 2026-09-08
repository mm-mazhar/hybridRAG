# Prompt — Set up git branch & commit policy for a Next.js project (pnpm)

You are a senior Next.js/TypeScript engineer. Set up the git workflow policy (branch
naming, commit messages, local hooks, CI gates) in the current **standalone Next.js
repository** (not a monorepo). The conventions mirror the ChatbotX repo. Create/modify
only the files listed below, run the listed commands, and finish with the verification
checklist. Report every file you created or changed.

## 0. Assumptions

- Package manager: **pnpm** (set `"packageManager": "pnpm@<latest>"` in `package.json`
  and add `"engines": { "node": ">=22" }`; create `.nvmrc` with the same Node version).
- Default branch is `main`.
- If the repo has no test runner yet, add **vitest** (`pnpm add -D vitest`) and make the
  CI test job match reality; if tests are explicitly out of scope, say so and skip the
  test job rather than adding a failing one.

## 1. Add tooling

```bash
pnpm add -D lefthook ultracite @biomejs/biome typescript
pnpm dlx ultracite init   # creates biome.json and wires deps
```

Ensure `package.json` scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "ultracite check",
    "fix": "ultracite fix --unsafe",
    "check-types": "tsc --noEmit",
    "test": "vitest run"
  }
}
```

Update `biome.json` to extend ultracite presets (keep any repo-specific ignores):

```json
{
  "$schema": "./node_modules/@biomejs/biome/configuration_schema.json",
  "formatter": { "enabled": true, "indentStyle": "space" },
  "linter": { "enabled": true, "rules": { "recommended": true } },
  "javascript": {
    "formatter": { "quoteStyle": "double", "semicolons": "asNeeded", "trailingCommas": "all" }
  },
  "extends": ["ultracite/biome/core", "ultracite/biome/next"]
}
```

## 2. Decide the ONE type gate

Mirror ChatbotX's explicit trade-off — exactly one of these must be true, never zero,
never both silently drifting:

- **Option A (ChatbotX-style):** `next.config.ts` sets
  `typescript: { ignoreBuildErrors: true }` and CI's `check-types` job
  (`tsc --noEmit`) is the ONLY type gate. Add a comment in `next.config.ts` saying the
  CI job must never be removed without re-enabling build-time type-checking.
- **Option B (safer default):** leave `next build` type-checking enabled and use CI's
  type job as a fast pre-check.

Pick one, state the choice in your report, and configure accordingly.

## 3. Create `lefthook.yml` (repo root)

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
          echo "  Example: feat/instagram-channel"
          echo "  Example: fix/whatsapp-webhook"
          echo ""
          echo "Rename it with: git branch -m <new-name>"
          exit 1
        fi

pre-commit:
  jobs:
    - run: pnpm ultracite fix
      glob: "*.{js,ts,cjs,mjs,d.cts,d.mts,jsx,tsx,json,jsonc}"
      stage_fixed: true
    - name: typecheck
      run: pnpm check-types
      glob: "**/*.{ts,tsx}"

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
          echo "  Append ! before the colon to mark a breaking change: feat(auth)!: remove legacy login"
          echo "  Example: feat(auth): add OAuth2 login"
          echo ""
          echo "Got: $MSG"
          exit 1
        fi
```

Install hooks:

```bash
pnpm exec lefthook install
```

The npm distribution of lefthook auto-installs hooks on `pnpm install`; if it doesn't
in this setup, add `"postinstall": "lefthook install"` to `package.json` so every
contributor gets hooks after a fresh clone.

## 4. Create `.agents/rules/git.md` (canonical human-readable rules)

Use the same document as the Python prompt (commit format + types, branch naming with
the same exemptions, never commit to `main`, never `git add -A`/`--no-verify`/secrets,
PR title = commit format + issue reference, run `pnpm lint` and `pnpm check-types`
before opening a PR, update `CHANGELOG.md` on release tags). Copy it verbatim with the
commands swapped for `pnpm lint` / `pnpm --filter ... check-types` -> `pnpm check-types`.

Also add a **Git conventions** section to root `AGENTS.md` (create the file if
missing) that points agents at the canonical rules, ChatbotX-style:

```markdown
## Git conventions

See **`.agents/rules/git.md`** for the full canonical rules (commit format, branch
naming, staging, PRs, changelog). Agents MUST follow that file for any git,
branch, commit, or PR work. `main` only advances through squash-merged PRs
(`protect_main` ruleset).
```

Do not leave git policy only in `lefthook.yml`. Agents read `AGENTS.md` first.

## 5. Create `.github/workflows/ci.yml`

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
  check-types:
    name: Types
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7
      # Version comes from packageManager in package.json
      - uses: pnpm/action-setup@v6
      - uses: actions/setup-node@v7
        with:
          node-version: 24
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm check-types

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7
      - uses: pnpm/action-setup@v6
      - uses: actions/setup-node@v7
        with:
          node-version: 24
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint

  test:
    name: Tests
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7
      - uses: pnpm/action-setup@v6
      - uses: actions/setup-node@v7
        with:
          node-version: 24
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
```

If tests are out of scope (see �0), omit the `test` job and say so.

## 6. Create `.github/workflows/pr-labeler.yml`

Same as ChatbotX: `pull_request_target (opened, edited, reopened)`, `actions/github-script`,
and the exact `TYPE_MAP` from ChatbotX's `.github/workflows/pr-labeler.yml`
(`feat` -> feature, `fix|bugfix` -> bug, `refactor|perf` -> improvement, `!` variants add
`breaking-change`, plus docs/chore/ci/security/deps mappings). Labels are bootstrapped
once in repo settings; the workflow only applies them.

## 7. Create `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    groups:
      dev-dependencies:
        dependency-type: "development"
        update-types: ["minor", "patch"]
      production-minor-patch:
        dependency-type: "production"
        update-types: ["minor", "patch"]
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

If the app is Dockerized (`output: "standalone"` + Dockerfile), also add a `docker`
ecosystem entry per Dockerfile directory with Node major bumps ignored (mirror
ChatbotX's rationale comments).

## 8. Optional: release workflow

If the app is deployed as a Docker image, create `.github/workflows/release.yml`
mirroring ChatbotX's: trigger on `push: branches: [main]` + `tags: ["v*"]`, build with
`docker/build-push-action` and per-leg GHA cache scopes. If deployed to Vercel, skip
this file and note that deploys are platform-managed. Either way add
`.github/release.yml` (changelog categories) and a `CHANGELOG.md` skeleton.

## 9. Protect `main` the ChatbotX way — EXECUTE, do not only document

ChatbotX does **not** use classic Settings → Branches → Branch protection.
It uses **repository rulesets**. A README note alone leaves `main` unprotected.
**Create the rulesets in this step.** Need `admin` on the repo.

### ChatbotX `main` ideology (language-agnostic — copy the flow)

`main` is a merge target, not a working branch.

1. **Nothing lands on `main` except through a PR.** Direct push is blocked.
2. **PRs squash-merge only.** History on `main` is one commit per PR, titled
   like a conventional commit (`feat(scope): subject`). The PR title **is** the
   squash subject — keep it in commit format.
3. **`main` cannot be deleted or force-pushed** (`deletion` + `non_fast_forward`).
4. **CI is a gate on the PR, then a confirmation on `main`.**
   Workflow `on: pull_request` plus `on: push: branches: [main]`.
   After this policy PR merges, the next push to `main` is the first time
   Types / Lint / Tests appear on the default branch. Until `ci.yml` is on
   `main`, that branch has no new checks — do not treat that as "skip
   protection."
5. **Required reviews can be 0** so a solo maintainer can merge their own PR.
   ChatbotX sets `required_approving_review_count: 0` and
   `require_extra_approval_for_unattributed_changes: true`.
6. **Copilot reviews non-draft PRs to the default branch** (optional second
   ruleset). Keep PRs draft until you want that review.
   ChatbotX: `review_on_push: false`, `review_draft_pull_requests: false`.
7. **Do not commit to `main` locally.** Hooks allow the branch name `main`;
   GitHub rejects the push. Always `git checkout -b <type>/<description>`.

ChatbotX's live `protect_main` ruleset is PR + squash + no delete/force-push.
It does **not** require CI status checks. This prompt **does** require
`Types` / `Lint` / `Tests` (job `name:` fields in `ci.yml`) so a red PR
cannot merge. That is the one intentional overlay.

### 9a. Create `protect_main` (required)

Payload: `docs/Prompts/stackNextJs/protect_main.ruleset.json` (same JSON as below).

```bash
gh api repos/OWNER/REPO/rulesets --method POST --input docs/Prompts/stackNextJs/protect_main.ruleset.json
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

If tests were omitted in section 0 / 5, drop the `Tests` context from the ruleset
and say so in the report.

Verify: `gh api repos/OWNER/REPO/rulesets` shows `protect_main` with
`enforcement: active`. A direct `git push origin main` must be rejected.

### 9b. Copilot review ruleset (optional — ChatbotX has this)

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

### 9c. README note (still required)

Document that `main` is protected by the `protect_main` **ruleset** (not
classic branch protection): PRs only, squash merge, no delete/force-push,
required checks `Types` / `Lint` / `Tests`. Point at Settings → Rules.

## 10. Verification checklist (run all of these)

1. `pnpm exec lefthook install` succeeds; hooks exist in `.git/hooks`.
2. `git checkout -b "bad_branch_name"` -> rejected. `git branch -m feat/policy-setup` -> accepted.
3. `git commit --allow-empty -m "bad message"` -> rejected by commit-msg hook.
4. `git commit --allow-empty -m "feat: valid message"` -> passes.
5. Add a badly formatted `.tsx` file, stage it, commit -> `ultracite fix` auto-fixes and
   restages it; `pnpm check-types` runs.
6. `pnpm lint && pnpm check-types && pnpm test` pass locally (skip `pnpm test` if tests were omitted).
7. Push the branch and open a draft PR to confirm CI turns green, then report.
8. Root `AGENTS.md` has a **Git conventions** section pointing at `.agents/rules/git.md`.
9. `gh api repos/OWNER/REPO/rulesets` lists `protect_main` with `enforcement: active`.
10. Do **not** test by force-pushing `main`. Confirm in the GitHub UI (Settings → Rules)
    that PRs are required, squash-only, and `Types` / `Lint` / `Tests` are required.

## 11. Other misses to apply next time (not all Next.js-specific)

- **`AGENTS.md` must point at `.agents/rules/git.md`.** ChatbotX does this so
  agents load commit/branch/PR rules without being told. Creating `git.md`
  alone is not enough.
- **Windows leftover scripts.** Inline multiline `run: |` in `lefthook.yml` often
  dies under Git Bash `sh -c` (`syntax error: unexpected end of file`). Put
  branch-name and commit-msg bodies in `.lefthook/<hook>/*.sh` with `runner: bash`
  and LF line endings. Keep the same regexes. Add `"postinstall": "lefthook install"`.
- **`main` has no new CI until `ci.yml` is merged.** The workflow file on the
  feature branch does not run for the default branch. Protection + required
  checks still belong in this setup, not after "we see checks on main."
- **Do not use classic branch protection** if you are copying ChatbotX. Use
  rulesets (`protect_main`). Classic Settings → Branches is a different product.
- **Keep PRs draft** until you want Copilot review (ChatbotX Copilot ruleset
  skips drafts).
