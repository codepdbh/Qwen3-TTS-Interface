from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = APP_DIR / "config"
OUTPUTS_DIR = APP_DIR / "outputs"
MODELS_DIR = APP_DIR / "models"
GENERATED_DIR = OUTPUTS_DIR / "generated"
HISTORY_DIR = OUTPUTS_DIR / "history"
TEMP_DIR = OUTPUTS_DIR / "temp"
VOICES_DIR = OUTPUTS_DIR / "voices"
ASSETS_DIR = APP_DIR / "assets"
SETTINGS_PATH = CONFIG_DIR / "settings.json"
CSS_PATH = ASSETS_DIR / "app.css"

DEFAULT_PORT = 7860
DEFAULT_SAMPLE_RATE = 24000
DEFAULT_SEED_TEXT = "Hola, esta es una muestra de voz diseñada para sintesis de texto."

VOICE_DESIGN_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
BASE_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
FALLBACK_BASE_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"

SUPPORTED_LANGUAGES = [
    "Chinese",
    "English",
    "Japanese",
    "Korean",
    "German",
    "French",
    "Russian",
    "Portuguese",
    "Spanish",
    "Italian",
]

SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".flac",
    ".ogg",
}

VOICE_PROMPT_EXAMPLES = [
    "Voz femenina calida, pausada, tono narrativo, acento latino neutro",
    "Voz masculina grave, segura, formal, ritmo medio",
    "Voz juvenil alegre, clara, natural",
    "voz femenina suave, calida, tono pedagogico, ritmo pausado",
    "voz masculina energica, segura, tono formal",
    "voz infantil amable, clara, neutra",
]

APP_MODES_MARKDOWN = """
### Modos disponibles

- **Diseno de voz**: crea una voz nueva a partir de una descripcion textual usando `VoiceDesign`.
- **Clonacion de voz**: replica el timbre de un audio de referencia usando `Base`.
- **Diseno + Clonacion**: genera primero una voz semilla y luego la reutiliza como prompt de clonacion.
"""

NOTES_MARKDOWN = """
### Notas

- `VoiceDesign` disena una voz desde texto descriptivo.
- `Base` permite clonacion desde audio.
- El modo hibrido combina ambos.
- En CPU el tiempo de generacion puede ser alto.
- Audios de referencia limpios dan mejores resultados.
"""

CPU_WARNING_MARKDOWN = """
### Advertencia de rendimiento

Esta aplicacion esta pensada para ejecutarse en **CPU**. La primera carga del modelo y cada sintesis pueden tardar bastante tiempo, especialmente con los modelos de 1.7B.
"""

UI_HELP_TEXTS = {
    "clone_audio_tip": "Procura subir un audio claro, sin ruido excesivo y con voz bien aislada.",
    "clone_transcript_tip": "Si conoces la transcripcion, escribela para mejores resultados.",
    "hybrid_tip": "Este modo primero disena una voz y luego la reutiliza como referencia para la salida final.",
    "loading_model": "Cargando modelo por primera vez...",
    "generating_audio": "Generando audio...",
    "process_done": "Proceso finalizado",
    "process_error": "Error al generar audio",
}

DEFAULT_SETTINGS = {
    "app_name": "Qwen3 TTS Studio",
    "host": "127.0.0.1",
    "port": DEFAULT_PORT,
    "device": "cpu",
    "output_dir": "outputs/generated",
    "history_file": "outputs/history/history.json",
    "temp_dir": "outputs/temp",
    "voices_dir": "outputs/voices",
    "voices_file": "outputs/voices/voices.json",
    "models_dir": "models",
    "voice_design_local_dir": "models/voice_design",
    "base_local_dir": "models/base",
    "download_models_on_demand": True,
    "default_language": "Spanish",
    "voice_design_model": VOICE_DESIGN_MODEL_ID,
    "base_model": BASE_MODEL_ID,
    "share": False,
    "debug": True,
}
