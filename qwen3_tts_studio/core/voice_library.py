import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from core.audio_utils import ensure_directory, get_timestamp_string, safe_filename
from core.validators import validate_reference_audio, validate_reference_text, validate_voice_name


class VoiceLibraryManager:
    def __init__(self, voices_file: str | Path, voices_dir: str | Path) -> None:
        self.voices_file = Path(voices_file)
        self.voices_dir = Path(voices_dir)
        ensure_directory(self.voices_dir)
        ensure_directory(self.voices_file.parent)
        if not self.voices_file.exists():
            self.voices_file.write_text("[]", encoding="utf-8")

    def update_paths(self, voices_file: str | Path, voices_dir: str | Path) -> None:
        self.voices_file = Path(voices_file)
        self.voices_dir = Path(voices_dir)
        ensure_directory(self.voices_dir)
        ensure_directory(self.voices_file.parent)
        if not self.voices_file.exists():
            self.voices_file.write_text("[]", encoding="utf-8")

    def load_voices(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self.voices_file.read_text(encoding="utf-8"))
        except Exception:
            data = []
        if not isinstance(data, list):
            return []
        return data

    def save_voices(self, voices: list[dict[str, Any]]) -> None:
        self.voices_file.write_text(
            json.dumps(voices, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_voice(
        self,
        name: str,
        source_audio_path: str,
        reference_text: str | None = None,
        language: str | None = None,
        source_mode: str = "reference_audio",
        voice_prompt: str | None = None,
    ) -> dict[str, Any]:
        clean_name = validate_voice_name(name)
        valid_audio = validate_reference_audio(source_audio_path)
        clean_reference_text = validate_reference_text(reference_text)

        source_path = Path(valid_audio)
        target_name = f"voice_{get_timestamp_string()}_{safe_filename(clean_name, 30)}{source_path.suffix.lower() or '.wav'}"
        target_path = self.voices_dir / target_name
        shutil.copy2(source_path, target_path)

        record = {
            "id": uuid.uuid4().hex[:12],
            "name": clean_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "audio_path": str(target_path),
            "reference_text": clean_reference_text,
            "language": (language or "").strip() or None,
            "source_mode": source_mode,
            "voice_prompt": (voice_prompt or "").strip() or None,
        }

        voices = self.load_voices()
        voices.insert(0, record)
        self.save_voices(voices)
        return record

    def get_voice(self, voice_id: str) -> dict[str, Any] | None:
        for voice in self.load_voices():
            if voice.get("id") == voice_id:
                return voice
        return None

    def delete_voice(self, voice_id: str) -> bool:
        voices = self.load_voices()
        target = None
        remaining: list[dict[str, Any]] = []
        for voice in voices:
            if voice.get("id") == voice_id and target is None:
                target = voice
            else:
                remaining.append(voice)

        if target is None:
            return False

        audio_path = target.get("audio_path")
        if audio_path:
            try:
                Path(audio_path).unlink(missing_ok=True)
            except Exception:
                pass

        self.save_voices(remaining)
        return True

    def get_voice_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for voice in self.load_voices():
            rows.append(
                [
                    voice.get("id", ""),
                    voice.get("name", ""),
                    voice.get("created_at", ""),
                    voice.get("source_mode", ""),
                    "si" if voice.get("reference_text") else "no",
                    voice.get("audio_path", ""),
                ]
            )
        return rows
