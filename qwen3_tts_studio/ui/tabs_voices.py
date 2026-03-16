from pathlib import Path

import gradio as gr

from ui.components import (
    build_voice_selector_label,
    parse_voice_selector_label,
    saved_voice_detail_markdown,
    step_header_html,
    tab_header_html,
    text_card_html,
    tips_card_html,
)


def build_voices_tab(tts_service) -> None:
    with gr.Tab("Voces guardadas"):
        gr.HTML(
            tab_header_html(
                "Biblioteca local",
                "Administra tus voces reutilizables",
                "Aqui puedes revisar las voces que ya guardaste, previsualizarlas y borrar las que ya no quieras conservar.",
            )
        )

        voices = tts_service.list_saved_voices()
        voice_choices = [build_voice_selector_label(record) for record in voices]

        with gr.Row(elem_classes=["workspace-grid"]):
            with gr.Column(scale=7, elem_classes=["surface-card", "surface-main"]):
                gr.HTML(step_header_html(1, "Explora la biblioteca", "La tabla resume nombre, fecha, origen y si la voz tiene transcripcion asociada."))
                voices_table = gr.Dataframe(
                    headers=["ID", "Nombre", "Creada", "Origen", "Transcripcion", "Audio"],
                    value=tts_service.get_saved_voice_rows(),
                    interactive=False,
                    wrap=True,
                    label="Voces guardadas",
                )
                gr.HTML(step_header_html(2, "Selecciona una voz", "Al elegir una voz podras oirla y revisar sus metadatos en el panel derecho."))
                with gr.Row():
                    voice_selector = gr.Dropdown(
                        choices=voice_choices,
                        value=voice_choices[0] if voice_choices else None,
                        label="Seleccionar voz",
                    )
                    refresh_button = gr.Button("Refrescar", variant="secondary")
                    delete_button = gr.Button("Borrar voz", variant="stop")
                status_output = gr.Textbox(label="Estado", interactive=False)

            with gr.Column(scale=5, elem_classes=["surface-card", "surface-side"]):
                gr.HTML(
                    text_card_html(
                        "Para que sirve esta biblioteca",
                        "Las voces guardadas te permiten reutilizar referencias sin volver a subir el mismo audio en cada clonacion. Puedes crearlas desde la pestana de clonacion o desde la semilla del flujo hibrido.",
                        tone="accent",
                    )
                )
                gr.HTML(
                    tips_card_html(
                        "Buenas practicas",
                        [
                            "Usa nombres faciles de reconocer para cada voz.",
                            "Si una voz ya no te sirve, puedes borrarla desde aqui.",
                            "Borrar una voz tambien elimina su copia local en la biblioteca.",
                        ],
                    )
                )
                preview_audio = gr.Audio(label="Vista previa", type="filepath")
                details_output = gr.Markdown(saved_voice_detail_markdown(voices[0] if voices else None))

        voice_selector.change(
            fn=lambda selected, service=tts_service: _preview_saved_voice(selected, service),
            inputs=voice_selector,
            outputs=[preview_audio, details_output],
        )
        refresh_button.click(
            fn=lambda service=tts_service: _refresh_saved_voice_library(service),
            outputs=[voices_table, voice_selector, preview_audio, details_output, status_output],
        )
        delete_button.click(
            fn=lambda selected, service=tts_service: _delete_saved_voice(selected, service),
            inputs=voice_selector,
            outputs=[voices_table, voice_selector, preview_audio, details_output, status_output],
        )


def _preview_saved_voice(selected_label: str | None, tts_service):
    voice_id = parse_voice_selector_label(selected_label)
    voice = tts_service.get_saved_voice(voice_id) if voice_id else None
    if not voice:
        return None, "Selecciona una voz guardada para ver su detalle."
    path = voice.get("audio_path")
    return (path if path and Path(path).exists() else None), saved_voice_detail_markdown(voice)


def _refresh_saved_voice_library(tts_service):
    voices = tts_service.list_saved_voices()
    choices = [build_voice_selector_label(record) for record in voices]
    first_voice = voices[0] if voices else None
    first_audio = first_voice.get("audio_path") if first_voice else None
    return (
        tts_service.get_saved_voice_rows(),
        gr.update(choices=choices, value=choices[0] if choices else None),
        first_audio if first_audio and Path(first_audio).exists() else None,
        saved_voice_detail_markdown(first_voice),
        "Biblioteca actualizada.",
    )


def _delete_saved_voice(selected_label: str | None, tts_service):
    voice_id = parse_voice_selector_label(selected_label)
    if not voice_id:
        return (
            tts_service.get_saved_voice_rows(),
            gr.update(),
            None,
            "Selecciona una voz guardada para ver su detalle.",
            "No se borro ninguna voz.",
        )
    deleted = tts_service.delete_saved_voice(voice_id)
    voices = tts_service.list_saved_voices()
    choices = [build_voice_selector_label(record) for record in voices]
    first_voice = voices[0] if voices else None
    first_audio = first_voice.get("audio_path") if first_voice else None
    return (
        tts_service.get_saved_voice_rows(),
        gr.update(choices=choices, value=choices[0] if choices else None),
        first_audio if first_audio and Path(first_audio).exists() else None,
        saved_voice_detail_markdown(first_voice),
        "Voz eliminada." if deleted else "No se encontro la voz seleccionada.",
    )
