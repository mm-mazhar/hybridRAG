# Daily git commit, push, and pull cycle

You never work on `main`. A normal day is: sync `main` → branch → commit locally → push the branch → open a PR → wait for checks → squash-merge → pull `main`.

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

## Push the branch

The commit exists only on your machine until you push. `git branch --all` will show your branch locally and `remotes/origin/main`, but not `remotes/origin/<your-branch>` yet.

```bash
git push -u origin HEAD          # first time on this branch
git push                         # later commits on the same branch
```

`pre-push` runs `pytest`. Do not `git push origin main`.

After the first push, GitHub shows a banner like `<branch> had recent pushes` with **Compare & pull request**. That only means the remote branch exists. It is not a PR and not a merge. Later pushes to the same branch update the PR automatically.

## Open a pull request

Prefer the GitHub CLI. The GitHub **Compare & pull request** (or **New pull request**) button does the same thing.

```bash
gh pr create --title "feat(app): add sitemap timeout" --body "What changed and why."
```

Add `--draft` if you are not ready for review yet:

```bash
gh pr create --draft --title "feat(app): add sitemap timeout" --body "What changed and why."
```

- let it `ALL GREEN` on github
- **PR title** uses the same format as commits (`feat(scope): subject`). Squash-merge uses that title as the commit on `main`, so write a clear title even if a local commit was vague.
- `gh pr create` uses the current branch as the head and `main` as the base. It does not take a title as a positional argument — use `--title` and `--body`.
- Keep the PR **draft** until you want review. Copilot only reviews non-draft PRs.

To add more work to an existing draft, stay on the **same branch**. Do not open a new PR. GitHub will show **Squash and merge** disabled until the draft is marked ready — that is expected.

```bash
git add path/to/file
git commit -m "chore: describe this extra change"
git push
```

The draft PR updates on its own (new commit, checks run again). Do not run `gh pr ready` until you are done adding work.

If you opened a draft and now want review:

```bash
gh pr ready
```

`gh pr ready` only marks the current branch's draft PR as ready. It does **not** set the title. Skip it if you did not use `--draft`.

## Wait, then squash-merge

Do not merge as soon as the PR exists. Wait until required checks **Lint**, **Types**, and **Tests** are green.

Then squash-merge (GitHub UI **Squash and merge**, or CLI):

```bash
gh pr merge --squash --delete-branch
```

With no number, `gh pr merge` uses the PR for the **current branch**. It takes a PR number, URL, or branch name — not a title.

- `--squash` is required by repo policy. Do not merge-commit or rebase-merge.
- `--delete-branch` deletes the **remote** branch after merge. It does not delete your local branch.
- After merge, CI also runs on `main` as confirmation.

Check status while waiting:

```bash
gh pr checks
gh pr view
```

## Stay current with `main` (while the PR is still open)

If `main` moved while you were working:

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
git fetch --prune origin
```

Then start the next branch from the updated `main`.

`--delete-branch` already removed the branch **on GitHub**. `git branch -d` removes your **local** branch. `git branch --all` can still list `remotes/origin/feat/short-description` — that is a **stale remote-tracking ref** on your machine, not a live GitHub branch. `git fetch --prune origin` deletes those leftover `remotes/origin/...` names. GitHub showing only `main` is the source of truth.

`gh pr checks` and `gh pr view` look at a PR for the **current** branch. After you checkout `main`, they report `no pull requests found for branch "main"` even if the merged PR exists. That is expected. Use `gh pr view 6` (the PR number) to see a closed PR.

## What you do not do daily

- commit or push to `main` (you may `checkout`/`pull` it; GitHub rejects `push`)
- force-push `main` or other shared branches
- merge-commit or rebase-merge a PR (squash only)
- commit `.env` / secrets
- skip hooks (`--no-verify`)
- tag a release (`v*`) unless you intend to publish
- treat the GitHub “had recent pushes” banner as a finished PR

## When you actually want a PyPI release

1. On pypi.org → your account → Publishing → add a trusted publisher:
   1. Owner: `user-id`
   2. Repository: `<name>`
   3. Workflow: `release.yml`
   4. Environment: `pypi`
2. Then from `main`:
   - `git tag v0.1.0`
   - `git push origin v0.1.0`
