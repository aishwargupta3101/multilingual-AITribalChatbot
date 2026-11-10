# Step 2 — Tribal-language STT service

This is an additive ASR module. It does **not** modify or replace the existing
`backend/services/mms_asr_service.py` used by Manipuri (`mni`).

## Why adapter codes are not pre-enabled

The registry's broad ISO code is not proof that a checkpoint has a matching
MMS adapter. This service therefore fails closed until the exact adapter code
for the chosen language variety has been verified against `facebook/mms-1b-all`.

## Example (after verification)

```python
from backend.tribal_languages.stt_service import TribalMMSSTTService

service = TribalMMSSTTService(adapter_codes={"santali": "<verified-adapter-code>"})
with open("sample.wav", "rb") as f:
    result = service.transcribe("santali", f.read())
print(result.text)
```

Replace the placeholder only after confirming the adapter exists and checking
licensing. Do not use this example as evidence that Santali, Gondi, or Monpa is
already verified. For Monpa, choose the exact variety (e.g. Tawang or Kalaktang)
and verify that variety independently.

## Dependencies

The project already lists PyTorch, Transformers, NumPy, SoundFile, and SciPy.
No requirements file changes are needed for this step.

## Validation

- Empty audio is rejected.
- Unsupported/unconfigured adapter codes fail before model loading.
- Audio is converted to mono and resampled to 16 kHz.
- Models load lazily and are cached per model/adapter pair.
