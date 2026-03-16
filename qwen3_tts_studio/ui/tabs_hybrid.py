import gradio as gr

from core.constants import DEFAULT_SEED_TEXT, SUPPORTED_LANGUAGES, UI_HELP_TEXTS
from ui.components import step_header_html, tab_header_html, text_card_html, tips_card_html


def build_hybrid_tab(tts_service) -> None:
    def on_hybrid(text: str, language: str, voice_prompt: str, seed_text: str):
        yield from _run_hybrid_generator(text, language, voice_prompt, seed_text, tts_service)

    with gr.Tab("Diseno + Clonacion"):
        gr.HTML(
            tab_header_html(
                "Flujo hibrido",
                "Disena una voz, genera una semilla y reutilizala",
                "Este modo combina VoiceDesign y Base. Primero crea un clip semilla a partir de una descripcion de voz, luego usa esa muestra como referencia para sintetizar el texto final.",
            )
        )

        with gr.Row(elem_classes=["workspace-grid"]):
            with gr.Column(scale=7, elem_classes=["surface-card", "surface-main"]):
                gr.HTML(step_header_html(1, "Define la identidad vocal", "Describe la voz y el idioma que quieres usar en todo el flujo."))
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

                gr.HTML(step_header_html(2, "Escribe el texto final", "Este contenido se generara con la voz obtenida a partir de la semilla."))
                text_input = gr.Textbox(
                    label="Texto final",
                    lines=8,
                    placeholder="Escribe el texto final que quieres sintetizar.",
                )

                gr.HTML(step_header_html(3, "Ajusta la semilla si hace falta", "Puedes dejar el texto semilla por defecto o personalizarlo para orientar mejor la voz inicial."))
                seed_text_input = gr.Textbox(
                    label="Texto semilla (opcional)",
                    lines=4,
                    value=DEFAULT_SEED_TEXT,
                    placeholder="Si lo dejas vacio, se usara un texto semilla por defecto.",
                )

                with gr.Accordion("Entender este flujo paso a paso", open=False):
                    gr.HTML(
                        tips_card_html(
                            "Que sucede internamente",
                            [
                                "Primero se genera un clip semilla con VoiceDesign.",
                                "Despues esa semilla se convierte en referencia de clonacion.",
                                "Por ultimo se sintetiza el audio final con el texto objetivo.",
                            ],
                            tone="accent",
                        )
                    )

                hybrid_button = gr.Button("Generar con flujo hibrido", variant="primary")

            with gr.Column(scale=5, elem_classes=["surface-card", "surface-side"]):
                gr.HTML(
                    text_card_html(
                        "Que obtendras",
                        "Vas a recibir dos audios: la semilla intermedia y el resultado final. Si te gusta la semilla, puedes guardarla como voz reutilizable para futuras clonaciones.",
                        tone="accent",
                    )
                )
                status_output = gr.Textbox(label="Estado del proceso", lines=4, interactive=False)
                seed_audio_output = gr.Audio(label="Audio semilla", type="filepath")
                final_audio_output = gr.Audio(label="Audio final", type="filepath")
                final_download_output = gr.File(label="Descargar WAV final")
                with gr.Accordion("Ruta y detalle del resultado", open=False):
                    seed_path_output = gr.Textbox(label="Ruta del clip semilla", interactive=False)
                    final_path_output = gr.Textbox(label="Ruta del audio final", interactive=False)
                    details_output = gr.Textbox(label="Detalle", interactive=False, lines=5)
                with gr.Accordion("Guardar la semilla en la biblioteca", open=False):
                    save_voice_name_input = gr.Textbox(
                        label="Nombre para la voz semilla",
                        placeholder="Ejemplo: Voz institucional nueva",
                    )
                    save_seed_voice_button = gr.Button("Guardar voz semilla", variant="secondary")
                    save_seed_status_output = gr.Textbox(label="Guardado de voz", interactive=False)

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
        save_seed_voice_button.click(
            fn=lambda name, seed_path, seed_text, language, prompt, service=tts_service: _save_seed_voice(
                name, seed_path, seed_text, language, prompt, service
            ),
            inputs=[save_voice_name_input, seed_path_output, seed_text_input, language_input, voice_prompt_input],
            outputs=[save_seed_status_output],
        )


def _save_seed_voice(
    name: str,
    seed_path: str | None,
    seed_text: str | None,
    language: str,
    voice_prompt: str,
    tts_service,
):
    try:
        _, message = tts_service.save_voice_profile(
            name=name,
            source_audio_path=seed_path or "",
            reference_text=seed_text,
            language=language,
            source_mode="hybrid_seed",
            voice_prompt=voice_prompt,
        )
        return message
    except Exception as exc:
        return f"Error al guardar la voz semilla: {exc}"


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
