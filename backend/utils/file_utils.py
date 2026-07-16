from pathlib import Path
from backend.config.settings import settings

def ensure_upload_directory():
    Path(settings.UPLOAD_DIR).mkdir(
        parents=True,
        exist_ok=True
    )