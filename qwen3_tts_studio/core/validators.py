from pathlib import Path

from core.audio_utils import is_supported_audio_file
from core.constants import SUPPORTED_LANGUAGES


class ValidationError(ValueError):
    pass


def validate_text(text: str, field_name: str = "texto", min_length: int = 1, max_length: int = 1800) -> str:
    value = (text or "").strip()
    if not value:
        raise ValidationError(f"El campo {field_name} no puede estar vacio.")
    if len(value) < min_length:
        raise ValidationError(f"El campo {field_name} es demasiado corto.")
    if len(value) > max_length:
        raise ValidationError(f"El campo {field_name} supera el maximo recomendado de {max_length} caracteres.")
    return value


def validate_language(language: str) -> str:
    value = (language or "").strip()
    if value not in SUPPORTED_LANGUAGES:
        raise ValidationError("Selecciona un idioma valido.")
    return value


def validate_voice_prompt(voice_prompt: str) -> str:
    return validate_text(voice_prompt, field_name="descripcion de voz", min_length=3, max_length=400)


def validate_reference_audio(reference_audio_path: str) -> str:
    if not reference_audio_path:
        raise ValidationError("Debes subir un audio de referencia.")
    path = Path(reference_audio_path)
    if not path.exists():
        raise ValidationError("El audio de referencia no existe o no pudo leerse.")
    if not is_supported_audio_file(reference_audio_path):
        raise ValidationError("Formato de audio no soportado. Usa wav, mp3, m4a, flac u ogg.")
    return str(path)


def validate_reference_text(reference_text: str | None) -> str | None:
    clean = (reference_text or "").strip()
    if not clean:
        return None
    if len(clean) > 1000:
        raise ValidationError("La transcripcion de referencia es demasiado larga.")
    return clean


def validate_voice_name(name: str) -> str:
    return validate_text(name, field_name="nombre de la voz", min_length=2, max_length=80)

