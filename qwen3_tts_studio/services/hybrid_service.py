from pathlib import Path
from typing import Any

import numpy as np

from core.audio_utils import get_audio_duration_seconds, save_numpy_audio_to_wav
from core.constants import DEFAULT_SEED_TEXT
from core.validators import validate_language, validate_text, validate_voice_prompt


class HybridService:
    def __init__(self, model_manager, settings: dict[str, Any]) -> None:
        self.model_manager = model_manager
        self.settings = settings

    def update_settings(self, settings: dict[str, Any]) -> None:
        self.settings = settings

    def generate_hybrid(
        self,
        text: str,
        language: str,
        voice_prompt: str,
        seed_text: str | None = None,
    ) -> dict[str, Any]:
        clean_text = validate_text(text, field_name="texto objetivo")
        clean_language = validate_language(language)
        clean_prompt = validate_voice_prompt(voice_prompt)
        clean_seed_text = (seed_text or "").strip() or DEFAULT_SEED_TEXT

        design_model = self.model_manager.load_voice_design_model()
        base_model = self.model_manager.load_base_model()

        print("[HybridService] Generando clip semilla con VoiceDesign.")
        seed_wavs, seed_sample_rate = design_model.generate_voice_design(
            text=clean_seed_text,
            language=clean_language,
            instruct=clean_prompt,
            non_streaming_mode=True,
        )

        seed_audio = self._first_audio(seed_wavs)
        seed_output_path = save_numpy_audio_to_wav(
            audio_array=seed_audio,
            sample_rate=seed_sample_rate,
            output_dir=Path(self.settings["output_dir"]),
            prefix="hybrid_seed",
            filename_hint=clean_seed_text[:24],
        )
        seed_duration_estimate = get_audio_duration_seconds(seed_output_path)

        print("[HybridService] Creando prompt de clonacion reutilizable.")
        voice_clone_prompt = base_model.create_voice_clone_prompt(
            ref_audio=seed_output_path,
            ref_text=clean_seed_text,
            x_vector_only_mode=False,
        )

        print("[HybridService] Generando audio final con Base.")
        final_wavs, final_sample_rate = base_model.generate_voice_clone(
            text=clean_text,
            language=clean_language,
            voice_clone_prompt=voice_clone_prompt,
            non_streaming_mode=True,
        )

        final_audio = self._first_audio(final_wavs)
        output_path = save_numpy_audio_to_wav(
            audio_array=final_audio,
            sample_rate=final_sample_rate,
            output_dir=Path(self.settings["output_dir"]),
            prefix="hybrid",
            filename_hint=clean_text[:24],
        )
        duration_estimate = get_audio_duration_seconds(output_path)

        return {
            "seed_output_path": seed_output_path,
            "output_path": output_path,
            "sample_rate": final_sample_rate,
            "mode": "hybrid",
            "model": f"{self.settings['voice_design_model']} + {self.settings['base_model']}",
            "duration_estimate": duration_estimate,
            "seed_duration_estimate": seed_duration_estimate,
            "language": clean_language,
            "voice_prompt": clean_prompt,
            "seed_text": clean_seed_text,
        }

    @staticmethod
    def _first_audio(wavs: Any) -> np.ndarray:
        if isinstance(wavs, list):
            return np.asarray(wavs[0])
        return np.asarray(wavs)

