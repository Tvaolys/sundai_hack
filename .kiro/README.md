# .kiro — team agent harness

Committed on purpose: HACKACHUSETTS requires `/.kiro` at the repo root. Never gitignore it.

| Path | What |
|---|---|
| `steering/` | Always-loaded project rules: `product.md`, `tech.md`, `workflow.md`. Fill the TODOs first. |
| `specs/` | One folder per feature (requirements / design / tasks). `_template/` to copy. |
| `agents/` | `lead`, `executor`, `reviewer`, `debugger` (JSON configs). |
| `hooks/guard.py` | preToolUse guard: blocks push, history rewrites, `git add .`, writes outside repo, `.env` writes, gitignoring `.kiro`. |

## Agents

| Agent | Model | Can write | Role |
|---|---|---|---|
| `lead` | claude-opus-5.5 | `.kiro/specs/**` only | Drafts specs, dispatches parallel executors + reviewer via subagent |
| `executor` | claude-sonnet-5.5 | repo (not `.kiro` config) | One task → test → commit |
| `reviewer` | claude-sonnet-5.5 | nothing | Diff review + test run, ends with `VERDICT:` |
| `debugger` | claude-opus-5.5 | repo (not `.kiro` config) | Reproduce → minimal fix → commit |

## Use

```bash
kiro-cli chat --agent lead        # "draft a spec for <idea>" → approve → "run the next batch"
kiro-cli chat --agent executor    # hand it a single task directly
kiro-cli chat --agent reviewer    # "review the last 3 commits"
```

`ctrl+g` in the TUI shows running subagent stages. Agents commit locally; humans `git pull --rebase && git push`.
