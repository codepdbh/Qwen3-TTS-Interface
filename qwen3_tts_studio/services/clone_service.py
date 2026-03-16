from pathlib import Path
from typing import Any

import numpy as np

from core.audio_utils import copy_input_audio, get_audio_duration_seconds, save_numpy_audio_to_wav
from core.validators import (
    validate_language,
    validate_reference_audio,
    validate_reference_text,
    validate_text,
)


class CloneService:
    def __init__(self, model_manager, settings: dict[str, Any]) -> None:
        self.model_manager = model_manager
        self.settings = settings

    def update_settings(self, settings: dict[str, Any]) -> None:
        self.settings = settings

    def generate_voice_clone(
        self,
        text: str,
        language: str,
        reference_audio_path: str,
        reference_text: str | None = None,
    ) -> dict[str, Any]:
        clean_text = validate_text(text, field_name="texto objetivo")
        clean_language = validate_language(language)
        valid_reference_audio = validate_reference_audio(reference_audio_path)
        clean_reference_text = validate_reference_text(reference_text)

        copied_reference_path = copy_input_audio(valid_reference_audio, self.settings["temp_dir"])
        model = self.model_manager.load_base_model()

        print("[CloneService] Generando clonacion de voz.")
        generation_kwargs: dict[str, Any] = {
            "text": clean_text,
            "language": clean_language,
            "ref_audio": copied_reference_path,
            "non_streaming_mode": True,
        }
        if clean_reference_text:
            generation_kwargs["ref_text"] = clean_reference_text
            generation_kwargs["x_vector_only_mode"] = False
        else:
            generation_kwargs["x_vector_only_mode"] = True

        # TODO: integrar ASR opcional con Whisper para inferir ref_text cuando falte.
        wavs, sample_rate = model.generate_voice_clone(**generation_kwargs)

        audio_array = self._first_audio(wavs)
        output_path = save_numpy_audio_to_wav(
            audio_array=audio_array,
            sample_rate=sample_rate,
            output_dir=Path(self.settings["output_dir"]),
            prefix="clone",
            filename_hint=clean_text[:24],
        )
        duration_estimate = get_audio_duration_seconds(output_path)

        return {
            "output_path": output_path,
            "sample_rate": sample_rate,
            "mode": "clone",
            "model": self.settings["base_model"],
            "duration_estimate": duration_estimate,
            "language": clean_language,
            "reference_audio_path": copied_reference_path,
            "reference_text": clean_reference_text,
            "clone_strategy": "icl" if clean_reference_text else "x_vector_only",
        }

    @staticmethod
    def _first_audio(wavs: Any) -> np.ndarray:
        if isinstance(wavs, list):
            return np.asarray(wavs[0])
        return np.asarray(wavs)

