# Multimodal Knowledge Assistant — v0.1 (Python backend)

Minimal working backend to boot a FastAPI server with a health endpoint.

## Quickstart

```bash
# 1) Create & activate a virtualenv (recommended)
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/health -> `{ "status": "ok", "version": "0.1" }`

## Structure

```
v0.1/
├─ src/
│  ├─ __init__.py
│  ├─ app.py
│  ├─ config.py
│  └─ routes/
│     ├─ __init__.py
│     └─ health.py
├─ tests/
│  └─ test_health.py
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ changelog.md
└─ pyproject.toml
```

## Notes

- Uses **FastAPI** + **Uvicorn** for a tiny HTTP server.
- `config.py` reads env vars with sensible defaults.
- `health.py` exposes `/health` for readiness checks.
- `pyproject.toml` pins the Python requirement and tool settings (ruff optional).
