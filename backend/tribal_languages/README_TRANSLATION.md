# Tribal Language Translation Service (Step 3)

This module is intentionally separate from the existing `backend/translation/` services. It does not modify or replace the Manipuri translation path.

## Behavior

- No translation pair is enabled by default.
- A pair must be explicitly verified and passed in `verified_pairs`.
- A compatible translation backend must be supplied as a callable.
- Monpa translation is blocked until a specific variety has been selected and validated.
- Unsupported pairs fail with a clear error instead of silently using an unrelated model.

## Example (only after evaluation)

```python
from backend.tribal_languages.translation_service import TribalTranslationService

def my_verified_backend(text: str, source: str, target: str) -> str:
    # Call a model/service only after its language pair is validated.
    raise NotImplementedError

service = TribalTranslationService(
    translator=my_verified_backend,
    verified_pairs=[("santali", "english")],  # Example only; do not enable without evaluation
    backend_name="my-tested-backend",
)
result = service.translate("sample", "santali", "english")
print(result.text)
```

The example backend is deliberately a placeholder. Do not connect NLLB merely because it is multilingual: check the actual tokenizer language tokens and evaluate the exact pair first.
