import gradio as gr

from core.constants import SUPPORTED_LANGUAGES, UI_HELP_TEXTS, VOICE_PROMPT_EXAMPLES
from ui.components import tab_header_html, tips_card_html


def build_generate_tab(tts_service) -> None:
    def on_generate(text: str, language: str, voice_prompt: str):
        yield from _run_design_generator(text, language, voice_prompt, tts_service)

    with gr.Tab("Diseno de voz"):
        gr.HTML(
            tab_header_html(
                "Modo VoiceDesign",
                "Disena una voz desde una descripcion escrita",
                "Usa el modelo Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign para crear una voz nueva a partir de estilo, tono y personalidad.",
            )
        )

        with gr.Row(elem_classes=["studio-workspace"]):
            with gr.Column(scale=2, elem_classes=["studio-panel", "studio-panel-main"]):
                text_input = gr.Textbox(
                    label="Texto a sintetizar",
                    lines=8,
                    placeholder="Escribe aqui el contenido que quieres convertir en voz.",
                )
                language_input = gr.Dropdown(
                    choices=SUPPORTED_LANGUAGES,
                    value=tts_service.settings["default_language"],
                    label="Idioma",
                )
                voice_prompt_input = gr.Textbox(
                    label="Descripcion de la voz",
                    lines=6,
                    placeholder="Ejemplo: voz femenina suave, calida, tono pedagogico, ritmo pausado",
                )
                preset_prompt = gr.Dropdown(
                    choices=VOICE_PROMPT_EXAMPLES,
                    label="Ejemplos rapidos",
                    value=VOICE_PROMPT_EXAMPLES[0],
                )
                apply_preset_button = gr.Button("Usar ejemplo", variant="secondary")
                generate_button = gr.Button("Generar", variant="primary")

            with gr.Column(scale=1, elem_classes=["studio-panel", "studio-panel-side"]):
                gr.HTML(
                    tips_card_html(
                        "Ejemplos de descripcion",
                        [
                            "Voz femenina calida, pausada, tono narrativo, acento latino neutro",
                            "Voz masculina grave, segura, formal, ritmo medio",
                            "Voz juvenil alegre, clara, natural",
                        ],
                    )
                )
                status_output = gr.Textbox(label="Estado del proceso", lines=4, interactive=False)
                audio_output = gr.Audio(label="Audio generado", type="filepath")
                download_output = gr.File(label="Descargar WAV")
                path_output = gr.Textbox(label="Ruta del archivo generado", interactive=False)
                details_output = gr.Textbox(label="Detalle", interactive=False, lines=4)

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
