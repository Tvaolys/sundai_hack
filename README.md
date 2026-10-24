# Who Gets Missed — Emergency Outreach planner

When a flood, heat wave, winter storm or power outage is coming, door-knock teams can only reach so
many homes. This tool uses live public data for any US county to show who to reach first, in which
languages, and who gets missed when capacity runs out. It is a planning aid only and never sends alerts.

## Run it
Open `demo/index.html` in Chrome, Edge or Firefox. One file, no install, no API keys.

For live Massachusetts power outages (Node 18+):

```bash
node demo/serve.js   # then open http://127.0.0.1:8765/
```

Full feature list, data sources and method: [`demo/README.md`](demo/README.md).

## Repo layout
| Path | What |
|---|---|
| `demo/` | The app (`index.html`), the optional local helper (`serve.js`) and its docs |
| `app/`, `tests/` | Python/FastAPI scaffold from the spec (`.venv/bin/python -m pytest -q`) |
| `.kiro/` | Kiro steering docs, specs, custom agents (lead / executor / reviewer / debugger) and guard hook |
