
"""Check registration of experimental Tribal Language Lab routes."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

EXPECTED = {
    ("GET", "/api/v1/tribal-languages/health"),
    ("GET", "/api/v1/tribal-languages/languages"),
    ("GET", "/api/v1/tribal-languages/languages/{language_code}"),
}


def collect_routes(routes, prefix=""):
    """Collect routes, including routers nested by FastAPI."""
    found = set()

    for route in routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)

        if path is not None and methods:
            for method in methods:
                found.add((method, path))

        original_router = getattr(route, "original_router", None)
        include_context = getattr(route, "include_context", None)

        if original_router is not None:
            nested_prefix = getattr(include_context, "prefix", "") or ""
            found.update(
                collect_routes(
                    original_router.routes,
                    prefix + nested_prefix,
                )
            )
        elif hasattr(route, "routes"):
            found.update(
                collect_routes(route.routes, prefix)
            )

    return {
        (method, prefix + path)
        for method, path in found
    }


def main() -> int:
    try:
        from backend.main import app
    except Exception as exc:
        print(f"Could not import backend.main: {type(exc).__name__}: {exc}")
        return 2

    actual = collect_routes(app.routes)
    missing = EXPECTED - actual

    if missing:
        print("Missing expected experimental routes:")
        for method, path in sorted(missing):
            print(f" - {method} {path}")
        print("\nNo changes were made to the application.")
        return 1

    print("All three experimental metadata routes are registered:")
    for method, path in sorted(EXPECTED):
        print(f" - {method} {path}")

    print("\nRoute registration check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
