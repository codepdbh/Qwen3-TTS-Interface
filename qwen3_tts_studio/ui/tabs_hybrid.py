import gradio as gr

from core.constants import DEFAULT_SEED_TEXT, SUPPORTED_LANGUAGES, UI_HELP_TEXTS


def build_hybrid_tab(tts_service) -> None:
    def on_hybrid(text: str, language: str, voice_prompt: str, seed_text: str):
        yield from _run_hybrid_generator(text, language, voice_prompt, seed_text, tts_service)

    with gr.Tab("Diseno + Clonacion"):
        gr.Markdown(
            """
            Este modo primero disena una voz, luego reutiliza esa muestra como referencia para la salida final.
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                text_input = gr.Textbox(
                    label="Texto final",
                    lines=8,
                    placeholder="Escribe el texto final que quieres sintetizar.",
                )
                language_input = gr.Dropdown(
                    choices=SUPPORTED_LANGUAGES,
                    value=tts_service.settings["default_language"],
                    label="Idioma",
                )
                voice_prompt_input = gr.Textbox(
                    label="Descripcion de la voz",
                    lines=6,
                    placeholder="Ejemplo: voz masculina energica, segura, tono formal",
                )
                seed_text_input = gr.Textbox(
                    label="Texto semilla (opcional)",
                    lines=4,
                    value=DEFAULT_SEED_TEXT,
                    placeholder="Si lo dejas vacio, se usara un texto semilla por defecto.",
                )
                hybrid_button = gr.Button("Generar con flujo hibrido", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown(UI_HELP_TEXTS["hybrid_tip"])
                status_output = gr.Textbox(label="Estado del proceso", lines=4, interactive=False)
                seed_audio_output = gr.Audio(label="Audio semilla", type="filepath")
                final_audio_output = gr.Audio(label="Audio final", type="filepath")
                seed_path_output = gr.Textbox(label="Ruta del clip semilla", interactive=False)
                final_path_output = gr.Textbox(label="Ruta del audio final", interactive=False)
                final_download_output = gr.File(label="Descargar WAV final")
                details_output = gr.Textbox(label="Detalle", interactive=False, lines=4)

        hybrid_button.click(
            fn=on_hybrid,
            inputs=[text_input, language_input, voice_prompt_input, seed_text_input],
            outputs=[
                status_output,
                seed_audio_output,
                final_audio_output,
                seed_path_output,
                final_path_output,
                final_download_output,
                details_output,
            ],
        )


def _run_hybrid_generator(text: str, language: str, voice_prompt: str, seed_text: str, tts_service):
    yield (
        f"{UI_HELP_TEXTS['loading_model']} Este flujo usa dos modelos y puede ser el mas lento en CPU.",
        None,
        None,
        "",
        "",
        None,
        UI_HELP_TEXTS["generating_audio"],
    )
    result = tts_service.run_hybrid(text, language, voice_prompt, seed_text)
    if result["ok"]:
        yield (
            result["status"],
            result["seed_output_path"],
            result["output_path"],
            result["seed_output_path"],
            result["output_path"],
            result["download_path"],
            result["details"],
        )
        return
    yield (
        result["status"],
        None,
        None,
        "",
        "",
        None,
        result["details"],
    )
