"""Read-only API for scheduled and currently configured tribal languages."""
from fastapi import APIRouter, HTTPException, Query

from backend.tribal_languages.indian_language_catalog import (
    get_language, list_languages, scheduled_language_keys,
)

router = APIRouter(prefix="/api/v1/indian-languages", tags=["Indian languages"])


@router.get("")
def get_languages(include_tribal: bool = Query(default=True)):
    """List catalog metadata and clearly labelled capability statuses."""
    items = list_languages(include_tribal=include_tribal)
    return {
        "count": len(items),
        "scheduled_language_count": len(scheduled_language_keys()),
        "languages": items,
        "note": "Catalog metadata does not guarantee that a model capability is operational.",
    }


@router.get("/{language_key}")
def get_language_detail(language_key: str):
    try:
        return get_language(language_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
