from pathlib import Path

import gradio as gr

from ui.components import build_history_selector_label, history_detail_markdown, parse_history_selector_label


def build_history_tab(tts_service) -> None:
    with gr.Tab("Historial"):
        gr.Markdown("Consulta generaciones anteriores, reproduce resultados guardados y limpia registros locales.")

        records = tts_service.get_history_records()
        selector_choices = [build_history_selector_label(record) for record in records]

        history_table = gr.Dataframe(
            headers=["ID", "Fecha", "Modo", "Texto", "Archivo generado", "Estado"],
            value=tts_service.get_history_rows(),
            interactive=False,
            wrap=True,
            label="Registros",
        )

        with gr.Row():
            selector = gr.Dropdown(
                choices=selector_choices,
                label="Seleccionar registro",
                value=selector_choices[0] if selector_choices else None,
            )
            refresh_button = gr.Button("Refrescar", variant="secondary")
            delete_button = gr.Button("Borrar item", variant="secondary")
            clear_button = gr.Button("Limpiar historial", variant="stop")

        preview_audio = gr.Audio(label="Reproducir desde historial", type="filepath")
        preview_path = gr.Textbox(label="Ruta del archivo", interactive=False)
        detail_markdown = gr.Markdown(history_detail_markdown(records[0] if records else None))
        status_output = gr.Textbox(label="Estado", interactive=False)

        selector.change(
            fn=lambda selected, service=tts_service: _preview_history_item(selected, service),
            inputs=selector,
            outputs=[preview_audio, preview_path, detail_markdown],
        )
        refresh_button.click(
            fn=lambda service=tts_service: _refresh_history(service),
            outputs=[history_table, selector, preview_audio, preview_path, detail_markdown, status_output],
        )
        delete_button.click(
            fn=lambda selected, service=tts_service: _delete_history_item(selected, service),
            inputs=selector,
            outputs=[history_table, selector, preview_audio, preview_path, detail_markdown, status_output],
        )
        clear_button.click(
            fn=lambda service=tts_service: _clear_history(service),
            outputs=[history_table, selector, preview_audio, preview_path, detail_markdown, status_output],
        )


def _refresh_history(tts_service):
    records = tts_service.get_history_records()
    choices = [build_history_selector_label(record) for record in records]
    return (
        tts_service.get_history_rows(),
        gr.update(choices=choices, value=choices[0] if choices else None),
        _existing_audio_path(records[0].get("archivo_salida_generado")) if records else None,
        records[0].get("archivo_salida_generado", "") if records else "",
        history_detail_markdown(records[0] if records else None),
        "Historial actualizado.",
    )


def _delete_history_item(selected_label: str | None, tts_service):
    record_id = parse_history_selector_label(selected_label)
    if not record_id:
        return (
            tts_service.get_history_rows(),
            gr.update(),
            None,
            "",
            "Selecciona un registro para borrarlo.",
            "No se borro ningun registro.",
        )
    deleted = tts_service.delete_history_item(record_id)
    records = tts_service.get_history_records()
    choices = [build_history_selector_label(record) for record in records]
    return (
        tts_service.get_history_rows(),
        gr.update(choices=choices, value=choices[0] if choices else None),
        _existing_audio_path(records[0].get("archivo_salida_generado")) if records else None,
        records[0].get("archivo_salida_generado", "") if records else "",
        history_detail_markdown(records[0] if records else None),
        "Registro eliminado." if deleted else "No se encontro el registro seleccionado.",
    )


def _clear_history(tts_service):
    tts_service.clear_history()
    return (
        [],
        gr.update(choices=[], value=None),
        None,
        "",
        "Selecciona un registro para ver su detalle.",
        "Historial limpiado.",
    )


def _preview_history_item(selected_label: str | None, tts_service):
    record_id = parse_history_selector_label(selected_label)
    record = tts_service.get_history_record(record_id) if record_id else None
    path = record.get("archivo_salida_generado") if record else None
    return _existing_audio_path(path), path or "", history_detail_markdown(record)


def _existing_audio_path(path: str | None) -> str | None:
    if not path:
        return None
    return path if Path(path).exists() else None

