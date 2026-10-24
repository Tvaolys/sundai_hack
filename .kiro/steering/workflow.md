# Workflow rules (always loaded)

## Work units
- Work comes from `.kiro/specs/<feature>/tasks.md`. One task at a time: implement, test, commit.
- Smallest change that satisfies the task's "done when". No drive-by refactors.
- If a task is bigger than ~15 minutes or the spec is ambiguous, stop and report. Don't improvise scope.

## Git
- Agents commit locally. Agents never push; humans push.
- Commit only the files you touched: `git add <paths>` then `git commit -m "..."`. Never `git add .`.
- Commit messages: imperative, one line, e.g. "add 311 SLA-miss scorer + test".
- If `git` reports `index.lock`, wait a few seconds and retry (parallel agents share the repo).
- Never: force push, `reset --hard`, `clean -f`, `branch -D`, rewriting history.
- Humans: `git pull --rebase` before `git push`. Four people share `main`.

## Safety
- Never edit outside this repo. Never install global packages; use a local venv / node_modules.
- Never write secrets to the repo. API keys go in `.env` (gitignored).

## Reporting
End every task with: what changed (files), test command + result, anything surprising.
