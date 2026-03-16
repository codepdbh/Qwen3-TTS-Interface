import json
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from core.audio_utils import ensure_directory
from core.constants import APP_DIR, DEFAULT_SETTINGS, SETTINGS_PATH
from core.device import get_default_device
from core.history_manager import HistoryManager
from core.model_manager import ModelManager
from services.clone_service import CloneService
from services.design_service import DesignService
from services.hybrid_service import HybridService


class TTSService:
    def __init__(self, settings_path: str | Path = SETTINGS_PATH) -> None:
        self.settings_path = Path(settings_path)
        self.settings = self._load_settings()
        self.model_manager = ModelManager(self.settings)
        self.history_manager = HistoryManager(self.settings["history_file"])
        self.design_service = DesignService(self.model_manager, self.settings)
        self.clone_service = CloneService(self.model_manager, self.settings)
        self.hybrid_service = HybridService(self.model_manager, self.settings)

    def run_design(self, text: str, language: str, voice_prompt: str) -> dict[str, Any]:
        try:
            result = self.design_service.generate_voice_design(text, language, voice_prompt)
            self._add_history_record(
                mode="design",
                text=text,
                language=language,
                voice_description=voice_prompt,
                reference_file=None,
                result=result,
                status="ok",
            )
            return {
                "ok": True,
                "status": "Proceso finalizado",
                "output_path": result["output_path"],
                "download_path": result["output_path"],
                "details": self._success_message(result),
            }
        except Exception as exc:
            self._log_exception("design", exc)
            self._add_history_record(
                mode="design",
                text=text,
                language=language,
                voice_description=voice_prompt,
                reference_file=None,
                result={},
                status="error",
                error_message=str(exc),
            )
            return self._error_response(exc)

    def run_clone(
        self,
        text: str,
        language: str,
        reference_audio_path: str,
        reference_text: str | None = None,
    ) -> dict[str, Any]:
        try:
            result = self.clone_service.generate_voice_clone(text, language, reference_audio_path, reference_text)
            self._add_history_record(
                mode="clone",
                text=text,
                language=language,
                voice_description=None,
                reference_file=result.get("reference_audio_path"),
                result=result,
                status="ok",
            )
            return {
                "ok": True,
                "status": "Proceso finalizado",
                "output_path": result["output_path"],
                "download_path": result["output_path"],
                "details": self._success_message(result),
            }
        except Exception as exc:
            self._log_exception("clone", exc)
            self._add_history_record(
                mode="clone",
                text=text,
                language=language,
                voice_description=None,
                reference_file=reference_audio_path,
                result={},
                status="error",
                error_message=str(exc),
            )
            return self._error_response(exc)

    def run_hybrid(
        self,
        text: str,
        language: str,
        voice_prompt: str,
        seed_text: str | None = None,
    ) -> dict[str, Any]:
        try:
            result = self.hybrid_service.generate_hybrid(text, language, voice_prompt, seed_text)
            self._add_history_record(
                mode="hybrid",
                text=text,
                language=language,
                voice_description=voice_prompt,
                reference_file=result.get("seed_output_path"),
                result=result,
                status="ok",
            )
            return {
                "ok": True,
                "status": "Proceso finalizado",
                "output_path": result["output_path"],
                "seed_output_path": result["seed_output_path"],
                "download_path": result["output_path"],
                "seed_download_path": result["seed_output_path"],
                "details": self._success_message(result),
            }
        except Exception as exc:
            self._log_exception("hybrid", exc)
            self._add_history_record(
                mode="hybrid",
                text=text,
                language=language,
                voice_description=voice_prompt,
                reference_file=None,
                result={},
                status="error",
                error_message=str(exc),
            )
            return self._error_response(exc)

    def get_history_rows(self) -> list[list[str]]:
        return self.history_manager.get_history_dataframe_like()

    def get_history_records(self) -> list[dict[str, Any]]:
        return self.history_manager.load_history()

    def get_history_record(self, record_id: str) -> dict[str, Any] | None:
        return self.history_manager.get_record(record_id)

    def delete_history_item(self, record_id: str) -> bool:
        return self.history_manager.delete_history_item(record_id)

    def clear_history(self) -> None:
        self.history_manager.clear_history()

    def unload_models(self) -> dict[str, Any]:
        self.model_manager.unload_models()
        return self.get_model_status()

    def get_model_status(self) -> dict[str, Any]:
        return self.model_manager.get_loaded_models_status()

    def reload_settings(self) -> dict[str, Any]:
        self.settings = self._load_settings()
        self.model_manager.update_settings(self.settings)
        self.history_manager.update_history_file(self.settings["history_file"])
        self.design_service.update_settings(self.settings)
        self.clone_service.update_settings(self.settings)
        self.hybrid_service.update_settings(self.settings)
        return self.get_settings_summary()

    def get_settings_summary(self) -> dict[str, Any]:
        return {
            "app_name": self.settings["app_name"],
            "host": self.settings["host"],
            "port": self.settings["port"],
            "device": self.settings["device"],
            "output_dir": self.settings["output_dir"],
            "history_file": self.settings["history_file"],
            "temp_dir": self.settings["temp_dir"],
            "models_dir": self.settings["models_dir"],
            "voice_design_local_dir": self.settings["voice_design_local_dir"],
            "base_local_dir": self.settings["base_local_dir"],
            "download_models_on_demand": self.settings["download_models_on_demand"],
            "voice_design_model": self.settings["voice_design_model"],
            "base_model": self.settings["base_model"],
            "share": self.settings["share"],
            "debug": self.settings["debug"],
        }

    def _load_settings(self) -> dict[str, Any]:
        loaded = json.loads(self.settings_path.read_text(encoding="utf-8"))
        settings = {**DEFAULT_SETTINGS, **loaded}
        settings["device"] = settings.get("device") or get_default_device()
        settings["output_dir"] = str(self._resolve_project_path(settings["output_dir"]))
        settings["history_file"] = str(self._resolve_project_path(settings["history_file"]))
        settings["temp_dir"] = str(self._resolve_project_path(settings["temp_dir"]))
        settings["models_dir"] = str(self._resolve_project_path(settings["models_dir"]))
        settings["voice_design_local_dir"] = str(self._resolve_project_path(settings["voice_design_local_dir"]))
        settings["base_local_dir"] = str(self._resolve_project_path(settings["base_local_dir"]))
        ensure_directory(settings["output_dir"])
        ensure_directory(Path(settings["history_file"]).parent)
        ensure_directory(settings["temp_dir"])
        ensure_directory(settings["models_dir"])
        ensure_directory(settings["voice_design_local_dir"])
        ensure_directory(settings["base_local_dir"])
        return settings

    def download_all_models(self, force_download: bool = False) -> tuple[dict[str, Any], str]:
        paths = self.model_manager.download_all_models(force_download=force_download)
        mode_text = "actualizados a la fuerza" if force_download else "descargados o verificados"
        return (
            self.get_model_status(),
            f"Modelos {mode_text}. VoiceDesign: {paths['voice_design']} | Base: {paths['base']}",
        )

    def download_voice_design_model(self, force_download: bool = False) -> tuple[dict[str, Any], str]:
        path = self.model_manager.download_voice_design_model(force_download=force_download)
        return self.get_model_status(), f"VoiceDesign listo en: {path}"

    def download_base_model(self, force_download: bool = False) -> tuple[dict[str, Any], str]:
        path = self.model_manager.download_base_model(force_download=force_download)
        return self.get_model_status(), f"Base listo en: {path}"

    def _resolve_project_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path
        return (APP_DIR / path).resolve()

    def _add_history_record(
        self,
        mode: str,
        text: str,
        language: str,
        voice_description: str | None,
        reference_file: str | None,
        result: dict[str, Any],
        status: str,
        error_message: str | None = None,
    ) -> None:
        record = {
            "id": uuid.uuid4().hex[:12],
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modo": mode,
            "texto": (text or "").strip(),
            "idioma": (language or "").strip(),
            "descripcion_de_voz": (voice_description or "").strip() or None,
            "archivo_referencia": reference_file,
            "archivo_salida_generado": result.get("output_path"),
            "archivo_semilla": result.get("seed_output_path"),
            "duracion_aproximada": result.get("duration_estimate"),
            "modelo_usado": result.get("model"),
            "estado": status,
            "mensaje_error": error_message,
        }
        self.history_manager.add_history_record(record)

    @staticmethod
    def _success_message(result: dict[str, Any]) -> str:
        duration = result.get("duration_estimate")
        duration_text = f"{duration:.2f} s" if isinstance(duration, (int, float)) else "no disponible"
        model_name = result.get("model", "desconocido")
        return f"Audio generado correctamente. Modelo: {model_name}. Duracion aproximada: {duration_text}."

    @staticmethod
    def _error_response(exc: Exception) -> dict[str, Any]:
        return {
            "ok": False,
            "status": f"Error al generar audio: {exc}",
            "output_path": None,
            "download_path": None,
            "seed_output_path": None,
            "seed_download_path": None,
            "details": "Consulta la consola para mas detalle tecnico.",
        }

    @staticmethod
    def _log_exception(mode: str, exc: Exception) -> None:
        print(f"[TTSService] Error en modo {mode}: {exc}")
        print(traceback.format_exc())
