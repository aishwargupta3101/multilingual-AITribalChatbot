# Add these two lines to backend/main.py only. Keep all existing imports and routers.
from backend.tribal_languages.santali_onnx_router import router as santali_onnx_stt_router

# Add alongside the existing app.include_router(...) calls:
app.include_router(santali_onnx_stt_router)
