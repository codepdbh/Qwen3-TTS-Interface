import gradio as gr

from core.constants import CSS_PATH, SETTINGS_PATH
from services.tts_service import TTSService
from ui.components import app_header_html, footer_notes_html, tips_card_html
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
    theme = gr.themes.Base(
        primary_hue=gr.themes.colors.emerald,
        neutral_hue=gr.themes.colors.slate,
        font=["Segoe UI", "Trebuchet MS", "sans-serif"],
        font_mono=["Consolas", "Courier New", "monospace"],
    )

    with gr.Blocks(title=settings.get("app_name", "Qwen3 TTS Studio"), css=css, theme=theme) as demo:
        gr.HTML(app_header_html())
        gr.HTML(
            tips_card_html(
                "Notas importantes",
                [
                    "VoiceDesign disena una voz desde texto descriptivo.",
                    "Base permite clonacion desde audio.",
                    "El modo hibrido combina ambos enfoques.",
                    "En CPU la primera carga y la sintesis pueden tardar bastante.",
                    "Audios de referencia limpios suelen dar mejores resultados.",
                ],
            ),
            elem_classes=["top-note-strip"],
        )

        with gr.Tabs(elem_classes=["studio-tabs"]):
            build_generate_tab(tts_service)
            build_clone_tab(tts_service)
            build_hybrid_tab(tts_service)
            build_history_tab(tts_service)
            build_settings_tab(tts_service)

        gr.HTML(footer_notes_html())

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
