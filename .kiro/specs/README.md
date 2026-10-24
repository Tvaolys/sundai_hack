# Specs

One folder per feature: `.kiro/specs/<feature>/` with `requirements.md`, `design.md`, `tasks.md`.
Copy `_template/` to start, or ask the `lead` agent to draft one from an idea.

tasks.md format (the lead parses this to decide what can run in parallel):

```markdown
- [ ] T1: <short title>
  - Files: app/scorer.py, tests/test_scorer.py
  - Done when: <observable, testable outcome>
  - Depends on: none
```

Tasks with no overlapping Files and satisfied dependencies are dispatched to executors in parallel.
