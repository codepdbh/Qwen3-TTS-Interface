import gc
import traceback
from pathlib import Path
from typing import Any

import torch

from core.audio_utils import ensure_directory
from core.constants import BASE_MODEL_ID, FALLBACK_BASE_MODEL_ID, VOICE_DESIGN_MODEL_ID
from core.device import get_default_device, get_preferred_dtype

try:
    from qwen_tts import Qwen3TTSModel
except Exception as exc:  # pragma: no cover - depende del entorno del usuario
    Qwen3TTSModel = None
    QWEN_TTS_IMPORT_ERROR = exc
else:
    QWEN_TTS_IMPORT_ERROR = None

try:
    from huggingface_hub import snapshot_download
except Exception as exc:  # pragma: no cover - depende del entorno del usuario
    snapshot_download = None
    HF_HUB_IMPORT_ERROR = exc
else:
    HF_HUB_IMPORT_ERROR = None


class ModelManager:
    def __init__(self, settings: dict[str, Any]) -> None:
        self.settings = settings
        self.device = settings.get("device") or get_default_device()
        self.model_voice_design = None
        self.model_base = None

    def update_settings(self, settings: dict[str, Any]) -> None:
        self.settings = settings
        self.device = settings.get("device") or get_default_device()

    def load_voice_design_model(self):
        if self.model_voice_design is None:
            model_id = self.settings.get("voice_design_model", VOICE_DESIGN_MODEL_ID)
            print(f"[ModelManager] Cargando VoiceDesign por primera vez: {model_id}")
            self.model_voice_design = self._load_model(
                model_id=model_id,
                local_dir_key="voice_design_local_dir",
                auto_download=bool(self.settings.get("download_models_on_demand", True)),
            )
        return self.model_voice_design

    def load_base_model(self):
        if self.model_base is None:
            model_id = self.settings.get("base_model", BASE_MODEL_ID)
            print(f"[ModelManager] Cargando Base por primera vez: {model_id}")
            self.model_base = self._load_model(
                model_id=model_id,
                local_dir_key="base_local_dir",
                auto_download=bool(self.settings.get("download_models_on_demand", True)),
            )
        return self.model_base

    def download_voice_design_model(self, force_download: bool = False) -> str:
        return self._download_model_snapshot(
            model_id=self.settings.get("voice_design_model", VOICE_DESIGN_MODEL_ID),
            target_dir=self._get_local_dir("voice_design_local_dir", "voice_design"),
            force_download=force_download,
        )

    def download_base_model(self, force_download: bool = False) -> str:
        return self._download_model_snapshot(
            model_id=self.settings.get("base_model", BASE_MODEL_ID),
            target_dir=self._get_local_dir("base_local_dir", "base"),
            force_download=force_download,
        )

    def download_all_models(self, force_download: bool = False) -> dict[str, str]:
        return {
            "voice_design": self.download_voice_design_model(force_download=force_download),
            "base": self.download_base_model(force_download=force_download),
        }

    def unload_models(self) -> None:
        self.model_voice_design = None
        self.model_base = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("[ModelManager] Modelos descargados de memoria.")

    def get_loaded_models_status(self) -> dict[str, Any]:
        return {
            "device": self.device,
            "voice_design_model_id": self.settings.get("voice_design_model", VOICE_DESIGN_MODEL_ID),
            "base_model_id": self.settings.get("base_model", BASE_MODEL_ID),
            "fallback_base_model_id": FALLBACK_BASE_MODEL_ID,
            "voice_design_local_dir": str(self._get_local_dir("voice_design_local_dir", "voice_design")),
            "base_local_dir": str(self._get_local_dir("base_local_dir", "base")),
            "voice_design_downloaded": self._is_local_model_downloaded(
                self._get_local_dir("voice_design_local_dir", "voice_design")
            ),
            "base_downloaded": self._is_local_model_downloaded(
                self._get_local_dir("base_local_dir", "base")
            ),
            "download_models_on_demand": bool(self.settings.get("download_models_on_demand", True)),
            "voice_design_loaded": self.model_voice_design is not None,
            "base_loaded": self.model_base is not None,
        }

    def _load_model(self, model_id: str, local_dir_key: str, auto_download: bool):
        if Qwen3TTSModel is None:
            raise RuntimeError(
                "No se pudo importar `qwen_tts`. Instala las dependencias y vuelve a intentarlo."
            ) from QWEN_TTS_IMPORT_ERROR

        model_source = self._resolve_model_source(model_id, local_dir_key, auto_download)
        last_error: Exception | None = None
        attempts = self._build_load_attempts()

        for attempt_name, kwargs in attempts:
            try:
                print(f"[ModelManager] Intentando cargar {model_source} con modo '{attempt_name}'.")
                model = Qwen3TTSModel.from_pretrained(model_source, **kwargs)
                raw_model = getattr(model, "model", None)
                if raw_model is not None and hasattr(raw_model, "to"):
                    raw_model.to(self.device)
                print(f"[ModelManager] Modelo listo en {self.device}: {model_source}")
                return model
            except Exception as exc:  # pragma: no cover - depende del runtime real
                last_error = exc
                print(f"[ModelManager] Fallo de carga en modo '{attempt_name}': {exc}")

        error_text = "".join(traceback.format_exception_only(type(last_error), last_error)).strip() if last_error else "Error desconocido."
        raise RuntimeError(
            f"No se pudo cargar el modelo '{model_id}'. Revisa la conexion a Hugging Face, RAM disponible y dependencias instaladas. Detalle: {error_text}"
        ) from last_error

    def _resolve_model_source(self, model_id: str, local_dir_key: str, auto_download: bool) -> str:
        local_dir = self._get_local_dir(local_dir_key, model_id.split("/")[-1].lower())
        if self._is_local_model_downloaded(local_dir):
            print(f"[ModelManager] Usando modelo local persistente: {local_dir}")
            return str(local_dir)
        if auto_download:
            print(f"[ModelManager] No existe copia local. Se descargara en: {local_dir}")
            return self._download_model_snapshot(model_id=model_id, target_dir=local_dir, force_download=False)
        print("[ModelManager] No hay copia local persistente. Se intentara cargar desde Hugging Face.")
        return model_id

    def _download_model_snapshot(self, model_id: str, target_dir: Path, force_download: bool = False) -> str:
        if snapshot_download is None:
            raise RuntimeError(
                "No se pudo importar `huggingface_hub`. Instala las dependencias y vuelve a intentarlo."
            ) from HF_HUB_IMPORT_ERROR

        ensure_directory(target_dir)
        print(f"[ModelManager] Descargando modelo '{model_id}' en '{target_dir}'.")
        try:
            snapshot_download(
                repo_id=model_id,
                local_dir=str(target_dir),
                local_dir_use_symlinks=False,
                force_download=force_download,
            )
        except Exception as exc:  # pragma: no cover - depende del runtime real
            raise RuntimeError(
                f"No se pudo descargar el modelo '{model_id}' en '{target_dir}'. Revisa tu conexion, permisos y espacio en disco. Detalle: {exc}"
            ) from exc

        if not self._is_local_model_downloaded(target_dir):
            raise RuntimeError(
                f"La descarga de '{model_id}' termino sin dejar un modelo utilizable en '{target_dir}'."
            )
        print(f"[ModelManager] Modelo descargado y persistido en: {target_dir}")
        return str(target_dir)

    def _get_local_dir(self, setting_key: str, default_leaf: str) -> Path:
        configured = self.settings.get(setting_key)
        if configured:
            return Path(configured)
        return Path(self.settings.get("models_dir", "models")) / default_leaf

    @staticmethod
    def _is_local_model_downloaded(model_dir: Path) -> bool:
        if not model_dir.exists() or not model_dir.is_dir():
            return False
        has_config = (model_dir / "config.json").exists()
        has_processor = (model_dir / "preprocessor_config.json").exists() or (model_dir / "processor_config.json").exists()
        has_weights = (
            any(model_dir.glob("*.safetensors"))
            or any(model_dir.glob("*.bin"))
            or (model_dir / "model.safetensors.index.json").exists()
        )
        return has_config and has_processor and has_weights

    def _build_load_attempts(self) -> list[tuple[str, dict[str, Any]]]:
        dtype = get_preferred_dtype(self.device)
        attempts: list[tuple[str, dict[str, Any]]] = [
            (
                "preferido",
                {
                    "device_map": self.device,
                    "dtype": dtype,
                    "attn_implementation": None,
                    "low_cpu_mem_usage": True,
                },
            ),
            (
                "sin_device_map",
                {
                    "dtype": dtype,
                    "attn_implementation": None,
                },
            ),
            (
                "minimo",
                {},
            ),
        ]
        return attempts
