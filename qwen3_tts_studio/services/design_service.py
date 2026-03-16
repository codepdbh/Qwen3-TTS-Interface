from pathlib import Path
from typing import Any

import numpy as np

from core.audio_utils import get_audio_duration_seconds, save_numpy_audio_to_wav
from core.validators import validate_language, validate_text, validate_voice_prompt


class DesignService:
    def __init__(self, model_manager, settings: dict[str, Any]) -> None:
        self.model_manager = model_manager
        self.settings = settings

    def update_settings(self, settings: dict[str, Any]) -> None:
        self.settings = settings

    def generate_voice_design(self, text: str, language: str, voice_prompt: str) -> dict[str, Any]:
        clean_text = validate_text(text, field_name="texto")
        clean_language = validate_language(language)
        clean_prompt = validate_voice_prompt(voice_prompt)

        model = self.model_manager.load_voice_design_model()
        print("[DesignService] Generando audio desde descripcion de voz.")
        wavs, sample_rate = model.generate_voice_design(
            text=clean_text,
            language=clean_language,
            instruct=clean_prompt,
            non_streaming_mode=True,
        )

        audio_array = self._first_audio(wavs)
        output_path = save_numpy_audio_to_wav(
            audio_array=audio_array,
            sample_rate=sample_rate,
            output_dir=Path(self.settings["output_dir"]),
            prefix="design",
            filename_hint=clean_text[:24],
        )
        duration_estimate = get_audio_duration_seconds(output_path)

        return {
            "output_path": output_path,
            "sample_rate": sample_rate,
            "mode": "design",
            "model": self.settings["voice_design_model"],
            "duration_estimate": duration_estimate,
            "language": clean_language,
            "voice_prompt": clean_prompt,
        }

    @staticmethod
    def _first_audio(wavs: Any) -> np.ndarray:
        if isinstance(wavs, list):
            return np.asarray(wavs[0])
        return np.asarray(wavs)

