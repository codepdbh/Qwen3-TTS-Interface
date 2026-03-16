import gradio as gr

from core.constants import APP_MODES_MARKDOWN, CPU_WARNING_MARKDOWN, CSS_PATH, NOTES_MARKDOWN, SETTINGS_PATH
from services.tts_service import TTSService
from ui.tabs_clone import build_clone_tab
from ui.tabs_generate import build_generate_tab
from ui.tabs_history import build_history_tab
from ui.tabs_hybrid import build_hybrid_tab
from ui.tabs_settings import build_settings_tab


def load_css() -> str:
    if CSS_PATH.exists():
        return CSS_PATH.read_text(encoding="utf-8")
    return ""


def create_app() -> tuple[gr.Blocks, dict]:
    tts_service = TTSService(SETTINGS_PATH)
    settings = tts_service.get_settings_summary()
    css = load_css()

    with gr.Blocks(title=settings.get("app_name", "Qwen3 TTS Studio"), css=css, theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # Qwen3 TTS Studio
            Interfaz local en Gradio para trabajar con Qwen3-TTS en Windows usando CPU.
            """
        )
        gr.Markdown(APP_MODES_MARKDOWN)
        gr.Markdown(CPU_WARNING_MARKDOWN)

        with gr.Tabs():
            build_generate_tab(tts_service)
            build_clone_tab(tts_service)
            build_hybrid_tab(tts_service)
            build_history_tab(tts_service)
            build_settings_tab(tts_service)

        gr.Markdown(NOTES_MARKDOWN)

    return demo, settings


def main() -> None:
    demo, settings = create_app()
    host = settings.get("host", "127.0.0.1")
    port = int(settings.get("port", 7860))
    share = bool(settings.get("share", False))
    print(f"[App] Iniciando Qwen3 TTS Studio en http://{host}:{port}")
    demo.queue(default_concurrency_limit=1).launch(server_name=host, server_port=port, share=share)


if __name__ == "__main__":
    main()
