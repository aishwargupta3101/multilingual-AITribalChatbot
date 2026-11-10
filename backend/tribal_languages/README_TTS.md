# Tribal Language Lab — TTS Service (Step 4)

This module is an additive interface for experimental Gondi, Santali, and
Monpa text-to-speech. It does not replace existing TTS services and does not
download or initialize a model automatically.

## Files

- `tts_service.py`: request validation, backend delegation, and safe errors.
- `test_tribal_tts_service.py`: unit tests with a fake backend.

## Usage

```python
from backend.tribal_languages.tts_service import TribalTTSService

def verified_tts_backend(*, text: str, language: str) -> bytes:
    # Connect a real, verified model here. Return encoded audio bytes.
    raise NotImplementedError("Connect a compatible TTS model first")

service = TribalTTSService(
    backend=verified_tts_backend,
    enabled_languages={"gondi"},  # only after verifying this backend
)

result = service.synthesize("Example text", "gondi")
# result.audio contains the backend's audio payload
# result.content_type identifies the expected audio media type
```

Do not enable a language until the exact variety, writing system, model
checkpoint, model licence, and output quality have been checked. Monpa must
be tied to a specified variety; do not treat `twm`, `kkf`, and `tbo` as
interchangeable.

## Integration

This is a service module only. It is not registered with FastAPI and does not
alter the current frontend. API integration should happen after a real backend
has been verified and the project’s existing audio response format is known.

## Run tests

From the repository root:

```powershell
python -m unittest tests.test_tribal_tts_service -v
```
