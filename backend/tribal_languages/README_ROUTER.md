# Step 5 — FastAPI router integration

This step adds a **metadata-only** router. It does not yet run model inference.

## Files

- `backend/tribal_languages/router.py`
- `backend/tribal_languages/README_ROUTER.md`
- `tests/test_tribal_language_router.py`
- `main_py_integration_snippet.py` (example only; not a replacement for your `backend/main.py`)

## Install

Copy `router.py` and `README_ROUTER.md` into your existing
`backend/tribal_languages/` folder. Keep your current registry, STT, translation,
and TTS files. Copy the test file into `tests/`.

## Minimal change to `backend/main.py`

Add this import alongside your other router imports:

```python
from backend.tribal_languages.router import router as tribal_language_lab_router
```

Then add this registration alongside the other `app.include_router(...)` calls:

```python
app.include_router(tribal_language_lab_router)
```

Do not remove or reorder existing routers. This router uses the prefix
`/api/v1/tribal-languages`, so its routes are:

- `GET /api/v1/tribal-languages/health`
- `GET /api/v1/tribal-languages/languages`
- `GET /api/v1/tribal-languages/languages/{language_code}`

## Test

```powershell
python -m unittest tests.test_tribal_language_router -v
```

The endpoints report metadata only. STT, translation, and TTS remain disabled
until verified model backends are connected and evaluated.
