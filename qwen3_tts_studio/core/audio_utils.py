import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

from core.constants import SUPPORTED_AUDIO_EXTENSIONS


def ensure_directory(path: Path | str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_timestamp_string() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_filename(text: str, max_length: int = 48) -> str:
    normalized = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", normalized).strip("._-")
    cleaned = re.sub(r"_+", "_", cleaned)
    return (cleaned[:max_length] or "audio").lower()


def build_output_path(output_dir: Path | str, prefix: str, hint: str = "audio", suffix: str = ".wav") -> Path:
    directory = ensure_directory(output_dir)
    filename = f"{prefix}_{get_timestamp_string()}_{safe_filename(hint, 24)}{suffix}"
    return directory / filename


def save_numpy_audio_to_wav(
    audio_array: np.ndarray,
    sample_rate: int,
    output_dir: Path | str,
    prefix: str,
    filename_hint: str = "audio",
) -> str:
    output_path = build_output_path(output_dir, prefix=prefix, hint=filename_hint)
    sf.write(output_path, np.asarray(audio_array), sample_rate, subtype="PCM_16")
    return str(output_path)


def copy_input_audio(file_path: str, temp_dir: Path | str) -> str:
    source_path = Path(file_path)
    if not source_path.exists():
        raise FileNotFoundError("El audio de referencia no existe o ya no esta disponible.")

    target_dir = ensure_directory(temp_dir)
    extension = source_path.suffix.lower() or ".wav"
    target_path = target_dir / f"ref_{get_timestamp_string()}_{safe_filename(source_path.stem, 24)}{extension}"
    shutil.copy2(source_path, target_path)
    return str(target_path)


def is_supported_audio_file(file_path: str | None) -> bool:
    if not file_path:
        return False
    return Path(file_path).suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS


def get_audio_duration_seconds(file_path: str | Path) -> Optional[float]:
    try:
        info = sf.info(str(file_path))
        return float(info.duration)
    except Exception:
        return None

