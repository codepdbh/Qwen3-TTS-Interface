import gradio as gr

from core.constants import SUPPORTED_LANGUAGES, UI_HELP_TEXTS


def build_clone_tab(tts_service) -> None:
    def on_clone(text: str, language: str, reference_audio: str, reference_text: str):
        yield from _run_clone_generator(text, language, reference_audio, reference_text, tts_service)

    with gr.Tab("Clonacion de voz"):
        gr.Markdown(
            """
            Clona una voz a partir de un audio de referencia usando `Qwen/Qwen3-TTS-12Hz-1.7B-Base`.
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                text_input = gr.Textbox(
                    label="Texto objetivo",
                    lines=8,
                    placeholder="Escribe el texto que quieres generar con la voz de referencia.",
                )
                language_input = gr.Dropdown(
                    choices=SUPPORTED_LANGUAGES,
                    value=tts_service.settings["default_language"],
                    label="Idioma",
                )
                reference_audio_input = gr.Audio(
                    label="Audio de referencia",
                    sources=["upload"],
                    type="filepath",
                )
                reference_text_input = gr.Textbox(
                    label="Transcripcion del audio de referencia (opcional)",
                    lines=4,
                    placeholder="Si conoces la transcripcion, escribela aqui.",
                )
                clone_button = gr.Button("Clonar voz", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown(f"- {UI_HELP_TEXTS['clone_audio_tip']}")
                gr.Markdown(f"- {UI_HELP_TEXTS['clone_transcript_tip']}")
                status_output = gr.Textbox(label="Estado del proceso", lines=4, interactive=False)
                audio_output = gr.Audio(label="Audio clonado", type="filepath")
                download_output = gr.File(label="Descargar WAV")
                path_output = gr.Textbox(label="Ruta del archivo generado", interactive=False)
                details_output = gr.Textbox(label="Detalle", interactive=False, lines=4)

        clone_button.click(
            fn=on_clone,
            inputs=[text_input, language_input, reference_audio_input, reference_text_input],
            outputs=[status_output, audio_output, download_output, path_output, details_output],
        )


def _run_clone_generator(text: str, language: str, reference_audio: str, reference_text: str, tts_service):
    yield (
        f"{UI_HELP_TEXTS['loading_model']} El modo Base tambien puede tardar bastante en CPU.",
        None,
        None,
        "",
        UI_HELP_TEXTS["generating_audio"],
    )
    result = tts_service.run_clone(text, language, reference_audio, reference_text)
    if result["ok"]:
        yield (
            result["status"],
            result["output_path"],
            result["download_path"],
            result["output_path"],
            result["details"],
        )
        return
    yield (
        result["status"],
        None,
        None,
        "",
        result["details"],
    )
