import gradio as gr

from core.constants import SUPPORTED_LANGUAGES, UI_HELP_TEXTS, VOICE_PROMPT_EXAMPLES
from ui.components import step_header_html, tab_header_html, text_card_html, tips_card_html


def build_generate_tab(tts_service) -> None:
    def on_generate(text: str, language: str, voice_prompt: str):
        yield from _run_design_generator(text, language, voice_prompt, tts_service)

    with gr.Tab("Diseno de voz"):
        gr.HTML(
            tab_header_html(
                "Modo VoiceDesign",
                "Crea una voz nueva desde una descripcion escrita",
                "Este flujo te ayuda a definir el texto, elegir idioma y describir con claridad el timbre, la actitud y el ritmo de la voz antes de generar el audio final.",
            )
        )

        with gr.Row(elem_classes=["workspace-grid"]):
            with gr.Column(scale=7, elem_classes=["surface-card", "surface-main"]):
                gr.HTML(step_header_html(1, "Escribe el contenido", "Introduce el texto exacto que quieres sintetizar."))
                text_input = gr.Textbox(
                    label="Texto a sintetizar",
                    lines=9,
                    placeholder="Escribe aqui el contenido que quieres convertir en voz.",
                )

                gr.HTML(step_header_html(2, "Configura el idioma y un punto de partida", "Puedes arrancar desde un ejemplo y luego personalizarlo."))
                with gr.Row():
                    language_input = gr.Dropdown(
                        choices=SUPPORTED_LANGUAGES,
                        value=tts_service.settings["default_language"],
                        label="Idioma",
                    )
                    preset_prompt = gr.Dropdown(
                        choices=VOICE_PROMPT_EXAMPLES,
                        label="Ejemplo rapido",
                        value=VOICE_PROMPT_EXAMPLES[0],
                    )
                    apply_preset_button = gr.Button("Aplicar ejemplo", variant="secondary")

                gr.HTML(step_header_html(3, "Describe la personalidad vocal", "Especifica timbre, energia, edad aproximada, ritmo o acento."))
                voice_prompt_input = gr.Textbox(
                    label="Descripcion de la voz",
                    lines=7,
                    placeholder="Ejemplo: voz femenina suave, calida, tono pedagogico, ritmo pausado",
                )

                with gr.Accordion("Ver ejemplos y consejos para el prompt de voz", open=False):
                    gr.HTML(
                        tips_card_html(
                            "Prompts que suelen funcionar bien",
                            [
                                "Voz femenina calida, pausada, tono narrativo, acento latino neutro",
                                "Voz masculina grave, segura, formal, ritmo medio",
                                "Voz juvenil alegre, clara, natural",
                                "Combina timbre + actitud + ritmo + acento para obtener resultados mas claros.",
                            ],
                            tone="accent",
                        )
                    )

                generate_button = gr.Button("Generar audio", variant="primary")

            with gr.Column(scale=5, elem_classes=["surface-card", "surface-side"]):
                gr.HTML(
                    text_card_html(
                        "Resultado esperado",
                        "Obtendras un archivo WAV, una previsualizacion directa en el navegador y el detalle basico del proceso para saber que modelo se uso.",
                        tone="accent",
                    )
                )
                status_output = gr.Textbox(label="Estado del proceso", lines=4, interactive=False)
                audio_output = gr.Audio(label="Audio generado", type="filepath")
                download_output = gr.File(label="Descargar WAV")
                with gr.Accordion("Ruta y detalle del resultado", open=False):
                    path_output = gr.Textbox(label="Ruta del archivo generado", interactive=False)
                    details_output = gr.Textbox(label="Detalle", interactive=False, lines=5)

        apply_preset_button.click(fn=lambda selected: selected, inputs=preset_prompt, outputs=voice_prompt_input)
        generate_button.click(
            fn=on_generate,
            inputs=[text_input, language_input, voice_prompt_input],
            outputs=[status_output, audio_output, download_output, path_output, details_output],
        )


def _run_design_generator(text: str, language: str, voice_prompt: str, tts_service):
    yield (
        f"{UI_HELP_TEXTS['loading_model']} En CPU puede tardar varios minutos.",
        None,
        None,
        "",
        UI_HELP_TEXTS["generating_audio"],
    )
    result = tts_service.run_design(text, language, voice_prompt)
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
