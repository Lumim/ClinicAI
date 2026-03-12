from pathlib import Path
from uuid import uuid4

from app.core.constants import ALLOWED_FILE_EXTENSIONS


def validate_file_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_FILE_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    return ext


def generate_storage_filename(original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    return f"{uuid4()}{ext}"