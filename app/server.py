from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="emready")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


# Registered last so /api/* routes take precedence. app/static is created in T9;
# skip the mount when it does not exist yet so startup never crashes.
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
