from pathlib import Path

import gradio as gr

from core.constants import SUPPORTED_LANGUAGES, UI_HELP_TEXTS
from ui.components import (
    build_voice_selector_label,
    parse_voice_selector_label,
    saved_voice_detail_markdown,
    step_header_html,
    tab_header_html,
    text_card_html,
    tips_card_html,
)


CLONE_SOURCE_UPLOAD = "Subir audio nuevo"
CLONE_SOURCE_SAVED = "Usar voz guardada"


def build_clone_tab(tts_service) -> None:
    def on_clone(
        text: str,
        language: str,
        source_mode: str,
        saved_voice_label: str | None,
        reference_audio: str | None,
        reference_text: str | None,
    ):
        yield from _run_clone_generator(
            text=text,
            language=language,
            source_mode=source_mode,
            saved_voice_label=saved_voice_label,
            reference_audio=reference_audio,
            reference_text=reference_text,
            tts_service=tts_service,
        )

    with gr.Tab("Clonacion de voz"):
        gr.HTML(
            tab_header_html(
                "Modo Base",
                "Clona una voz desde un audio nuevo o una voz guardada",
                "Primero elige la fuente de voz. Despues escribe el texto objetivo y genera el resultado con el modelo Base. Si te conviene, puedes guardar nuevas referencias para reutilizarlas despues.",
            )
        )

        saved_voices = tts_service.list_saved_voices()
        saved_voice_choices = [build_voice_selector_label(record) for record in saved_voices]

        with gr.Row(elem_classes=["workspace-grid"]):
            with gr.Column(scale=7, elem_classes=["surface-card", "surface-main"]):
                gr.HTML(step_header_html(1, "Elige la fuente de voz", "Decide si usaras un audio nuevo o una voz guardada."))
                source_mode_input = gr.Radio(
                    choices=[CLONE_SOURCE_UPLOAD, CLONE_SOURCE_SAVED],
                    value=CLONE_SOURCE_UPLOAD,
                    label="Fuente de voz",
                )
                source_summary = gr.HTML(
                    text_card_html(
                        "Fuente actual",
                        "Sube un audio nuevo, ajusta la transcripcion si la conoces y, si quieres, guardalo para usarlo otra vez mas adelante.",
                        tone="accent",
                    )
                )

                with gr.Group(visible=False) as saved_voice_group:
                    with gr.Row():
                        saved_voice_selector = gr.Dropdown(
                            choices=saved_voice_choices,
                            value=saved_voice_choices[0] if saved_voice_choices else None,
                            label="Voz guardada",
                        )
                        refresh_saved_voices_button = gr.Button("Actualizar voces", variant="secondary")

                with gr.Group(visible=True) as upload_voice_group:
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
                    with gr.Accordion("Guardar esta referencia en la biblioteca", open=False):
                        save_voice_name_input = gr.Textbox(
                            label="Nombre para guardar esta voz",
                            placeholder="Ejemplo: Narradora principal",
                        )
                        save_voice_button = gr.Button("Guardar esta voz", variant="secondary")
                        save_voice_status_output = gr.Textbox(label="Guardado de voz", interactive=False)

                gr.HTML(step_header_html(2, "Escribe el texto que vas a generar", "Este sera el contenido final sintetizado con la voz elegida."))
                text_input = gr.Textbox(
                    label="Texto objetivo",
                    lines=8,
                    placeholder="Escribe el texto que quieres generar con la voz elegida.",
                )
                language_input = gr.Dropdown(
                    choices=SUPPORTED_LANGUAGES,
                    value=tts_service.settings["default_language"],
                    label="Idioma",
                )

                clone_button = gr.Button("Clonar voz", variant="primary")

            with gr.Column(scale=5, elem_classes=["surface-card", "surface-side"]):
                gr.HTML(
                    tips_card_html(
                        "Consejos rapidos",
                        [
                            UI_HELP_TEXTS["clone_audio_tip"],
                            UI_HELP_TEXTS["clone_transcript_tip"],
                            "Las voces guardadas sirven para reutilizar el mismo timbre sin volver a subir el audio.",
                        ],
                        tone="accent",
                    )
                )
                saved_voice_preview = gr.Audio(
                    label="Vista previa de la fuente guardada",
                    type="filepath",
                    visible=False,
                )
                saved_voice_details = gr.Markdown(
                    "Selecciona una voz guardada para ver su detalle.",
                    visible=False,
                )
                status_output = gr.Textbox(label="Estado del proceso", lines=4, interactive=False)
                audio_output = gr.Audio(label="Audio clonado", type="filepath")
                download_output = gr.File(label="Descargar WAV")
                with gr.Accordion("Ruta y detalle del resultado", open=False):
                    path_output = gr.Textbox(label="Ruta del archivo generado", interactive=False)
                    details_output = gr.Textbox(label="Detalle", interactive=False, lines=5)

        source_mode_input.change(
            fn=_toggle_clone_source,
            inputs=source_mode_input,
            outputs=[source_summary, saved_voice_group, upload_voice_group, saved_voice_preview, saved_voice_details],
        )
        saved_voice_selector.change(
            fn=lambda selected, service=tts_service: _load_saved_voice_preview(selected, service),
            inputs=saved_voice_selector,
            outputs=[saved_voice_preview, saved_voice_details],
        )
        refresh_saved_voices_button.click(
            fn=lambda service=tts_service: _refresh_saved_voices(service),
            outputs=[saved_voice_selector, saved_voice_preview, saved_voice_details],
        )
        save_voice_button.click(
            fn=lambda name, audio, ref_text, language, service=tts_service: _save_uploaded_voice(
                name, audio, ref_text, language, service
            ),
            inputs=[save_voice_name_input, reference_audio_input, reference_text_input, language_input],
            outputs=[save_voice_status_output, saved_voice_selector, saved_voice_preview, saved_voice_details],
        )
        clone_button.click(
            fn=on_clone,
            inputs=[
                text_input,
                language_input,
                source_mode_input,
                saved_voice_selector,
                reference_audio_input,
                reference_text_input,
            ],
            outputs=[status_output, audio_output, download_output, path_output, details_output],
        )


def _toggle_clone_source(source_mode: str):
    use_saved = source_mode == CLONE_SOURCE_SAVED
    summary_html = text_card_html(
        "Fuente actual",
        "Estas reutilizando una voz guardada de tu biblioteca local. Verifica la vista previa y luego genera el texto objetivo."
        if use_saved
        else "Sube un audio nuevo, completa la transcripcion si la conoces y guardalo solo si quieres reutilizarlo mas tarde.",
        tone="accent" if use_saved else "default",
    )
    return (
        summary_html,
        gr.update(visible=use_saved),
        gr.update(visible=not use_saved),
        gr.update(visible=use_saved),
        gr.update(visible=use_saved),
    )


def _load_saved_voice_preview(saved_voice_label: str | None, tts_service):
    voice_id = parse_voice_selector_label(saved_voice_label)
    voice = tts_service.get_saved_voice(voice_id) if voice_id else None
    if not voice:
        return None, "Selecciona una voz guardada para ver su detalle."
    audio_path = voice.get("audio_path")
    existing_audio = audio_path if audio_path and Path(audio_path).exists() else None
    return existing_audio, saved_voice_detail_markdown(voice)


def _refresh_saved_voices(tts_service):
    voices = tts_service.list_saved_voices()
    choices = [build_voice_selector_label(record) for record in voices]
    preview_path = voices[0]["audio_path"] if voices and Path(voices[0]["audio_path"]).exists() else None
    return (
        gr.update(choices=choices, value=choices[0] if choices else None),
        preview_path,
        saved_voice_detail_markdown(voices[0] if voices else None),
    )


def _save_uploaded_voice(name: str, audio_path: str | None, reference_text: str | None, language: str, tts_service):
    try:
        record, message = tts_service.save_voice_profile(
            name=name,
            source_audio_path=audio_path or "",
            reference_text=reference_text,
            language=language,
            source_mode="reference_audio",
        )
    except Exception as exc:
        return f"Error al guardar la voz: {exc}", gr.update(), None, "Selecciona una voz guardada para ver su detalle."

    voices = tts_service.list_saved_voices()
    choices = [build_voice_selector_label(item) for item in voices]
    selected_label = build_voice_selector_label(record)
    preview_path = record["audio_path"] if Path(record["audio_path"]).exists() else None
    return message, gr.update(choices=choices, value=selected_label), preview_path, saved_voice_detail_markdown(record)


def _run_clone_generator(
    text: str,
    language: str,
    source_mode: str,
    saved_voice_label: str | None,
    reference_audio: str | None,
    reference_text: str | None,
    tts_service,
):
    yield (
        f"{UI_HELP_TEXTS['loading_model']} El modo Base tambien puede tardar bastante en CPU.",
        None,
        None,
        "",
        UI_HELP_TEXTS["generating_audio"],
    )

    if source_mode == CLONE_SOURCE_SAVED:
        voice_id = parse_voice_selector_label(saved_voice_label)
        if not voice_id:
            yield ("Debes seleccionar una voz guardada.", None, None, "", "Elige una voz guardada o cambia a audio nuevo.")
            return
        result = tts_service.run_clone_with_saved_voice(text, language, voice_id)
    else:
        result = tts_service.run_clone(text, language, reference_audio or "", reference_text)

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
