import gradio as gr

from ui.components import (
    render_model_progress_html,
    render_runtime_snapshot_html,
    render_settings_snapshot_html,
    render_storage_snapshot_html,
    step_header_html,
    tab_header_html,
    text_card_html,
    tips_card_html,
)


def build_settings_tab(tts_service) -> None:
    def on_download_normal():
        yield from _download_models_generator(tts_service, force_download=False)

    def on_force_download():
        yield from _download_models_generator(tts_service, force_download=True)

    with gr.Tab("Configuracion"):
        gr.HTML(
            tab_header_html(
                "Entorno y modelos",
                "Revisa rutas, estado local y descargas persistentes",
                "Aqui puedes confirmar donde se guardan los archivos, comprobar si los modelos ya estan disponibles localmente y ejecutar acciones de mantenimiento sin salir de la app.",
            )
        )

        settings_summary = tts_service.get_settings_summary()
        model_status = tts_service.get_model_status()

        with gr.Row(elem_classes=["workspace-grid"]):
            with gr.Column(scale=5, elem_classes=["surface-card", "surface-side"]):
                gr.HTML(
                    text_card_html(
                        "Que puedes hacer aqui",
                        "Descarga una sola vez los modelos para reutilizarlos despues, recarga la configuracion desde disco y descarga los modelos de memoria cuando quieras liberar RAM sin borrar los archivos.",
                        tone="accent",
                    )
                )
                progress_html = gr.HTML(
                    value=render_model_progress_html(
                        model_status,
                        note="Si descargas los modelos una vez, la app intentara reutilizar esas copias locales despues.",
                    )
                )
                gr.HTML(
                    tips_card_html(
                        "Acciones disponibles",
                        [
                            "Recargar configuracion para leer de nuevo settings.json.",
                            "Desalojar modelos para liberar memoria sin borrar los archivos del disco.",
                            "Forzar actualizacion si quieres volver a descargar los modelos.",
                        ],
                    )
                )
                status_output = gr.Textbox(
                    label="Estado",
                    interactive=False,
                    value="Configuracion cargada. Usa esta pantalla para revisar rutas y gestionar modelos locales.",
                )
                with gr.Row():
                    reload_button = gr.Button("Recargar configuracion", variant="secondary")
                    unload_button = gr.Button("Desalojar modelos", variant="secondary")
                with gr.Row():
                    refresh_button = gr.Button("Actualizar estado", variant="secondary")
                    download_button = gr.Button("Descargar modelos", variant="primary")
                    force_download_button = gr.Button("Forzar actualizacion", variant="secondary")

            with gr.Column(scale=7, elem_classes=["surface-card", "surface-main"]):
                gr.HTML(step_header_html(1, "Configuracion de la aplicacion", "Resume el host, puerto, dispositivo y otras opciones activas."))
                settings_html = gr.HTML(render_settings_snapshot_html(settings_summary))
                gr.HTML(step_header_html(2, "Rutas de trabajo", "Muestra donde se guardan audios, historial, voces y modelos locales."))
                storage_html = gr.HTML(render_storage_snapshot_html(settings_summary))
                gr.HTML(step_header_html(3, "Estado de ejecucion", "Indica si los modelos estan descargados o cargados en memoria."))
                runtime_html = gr.HTML(render_runtime_snapshot_html(model_status))

        reload_button.click(
            fn=lambda service=tts_service: _reload_settings(service),
            outputs=[settings_html, storage_html, runtime_html, progress_html, status_output],
        )
        unload_button.click(
            fn=lambda service=tts_service: _unload_models(service),
            outputs=[settings_html, storage_html, runtime_html, progress_html, status_output],
        )
        refresh_button.click(
            fn=lambda service=tts_service: _refresh_status(service),
            outputs=[settings_html, storage_html, runtime_html, progress_html, status_output],
        )
        download_button.click(
            fn=on_download_normal,
            outputs=[settings_html, storage_html, runtime_html, progress_html, status_output],
        )
        force_download_button.click(
            fn=on_force_download,
            outputs=[settings_html, storage_html, runtime_html, progress_html, status_output],
        )


def _reload_settings(tts_service):
    settings = tts_service.reload_settings()
    model_status = tts_service.get_model_status()
    return (
        render_settings_snapshot_html(settings),
        render_storage_snapshot_html(settings),
        render_runtime_snapshot_html(model_status),
        render_model_progress_html(model_status),
        "Configuracion recargada desde settings.json.",
    )


def _unload_models(tts_service):
    model_status = tts_service.unload_models()
    settings = tts_service.get_settings_summary()
    return (
        render_settings_snapshot_html(settings),
        render_storage_snapshot_html(settings),
        render_runtime_snapshot_html(model_status),
        render_model_progress_html(model_status, note="Los archivos siguen en disco aunque los modelos ya no esten cargados en memoria."),
        "Modelos descargados de memoria.",
    )


def _refresh_status(tts_service):
    settings = tts_service.get_settings_summary()
    model_status = tts_service.get_model_status()
    return (
        render_settings_snapshot_html(settings),
        render_storage_snapshot_html(settings),
        render_runtime_snapshot_html(model_status),
        render_model_progress_html(model_status),
        "Estado actualizado.",
    )


def _download_models_generator(tts_service, force_download: bool):
    mode_text = "forzada" if force_download else "normal"
    initial_settings = tts_service.get_settings_summary()
    initial_status = tts_service.get_model_status()
    yield (
        render_settings_snapshot_html(initial_settings),
        render_storage_snapshot_html(initial_settings),
        render_runtime_snapshot_html(initial_status),
        render_model_progress_html(
            initial_status,
            active_label=f"Preparando descarga {mode_text}",
            percent_override=5,
            note="Se descargara primero VoiceDesign y luego Base.",
        ),
        "Preparando descarga de modelos...",
    )

    yield (
        render_settings_snapshot_html(initial_settings),
        render_storage_snapshot_html(initial_settings),
        render_runtime_snapshot_html(initial_status),
        render_model_progress_html(
            initial_status,
            active_label="Descargando VoiceDesign (1/2)",
            percent_override=15,
            note="Este paso puede tardar bastante la primera vez.",
        ),
        "Descargando modelo VoiceDesign...",
    )
    try:
        voice_status, voice_message = tts_service.download_voice_design_model(force_download=force_download)
    except Exception as exc:
        failed_settings = tts_service.get_settings_summary()
        failed_status = tts_service.get_model_status()
        yield (
            render_settings_snapshot_html(failed_settings),
            render_storage_snapshot_html(failed_settings),
            render_runtime_snapshot_html(failed_status),
            render_model_progress_html(
                failed_status,
                active_label="Error descargando VoiceDesign",
                percent_override=15,
                note="Revisa la conexion a internet, el espacio en disco o los permisos de escritura.",
            ),
            f"Error al descargar VoiceDesign: {exc}",
        )
        return

    current_settings = tts_service.get_settings_summary()
    yield (
        render_settings_snapshot_html(current_settings),
        render_storage_snapshot_html(current_settings),
        render_runtime_snapshot_html(voice_status),
        render_model_progress_html(
            voice_status,
            active_label="VoiceDesign descargado. Continuando con Base (2/2)",
            percent_override=55,
            note=voice_message,
        ),
        voice_message,
    )

    yield (
        render_settings_snapshot_html(current_settings),
        render_storage_snapshot_html(current_settings),
        render_runtime_snapshot_html(voice_status),
        render_model_progress_html(
            voice_status,
            active_label="Descargando Base (2/2)",
            percent_override=70,
            note="La app reutilizara esta copia local en futuros arranques.",
        ),
        "Descargando modelo Base...",
    )
    try:
        base_status, base_message = tts_service.download_base_model(force_download=force_download)
    except Exception as exc:
        failed_settings = tts_service.get_settings_summary()
        failed_status = tts_service.get_model_status()
        yield (
            render_settings_snapshot_html(failed_settings),
            render_storage_snapshot_html(failed_settings),
            render_runtime_snapshot_html(failed_status),
            render_model_progress_html(
                failed_status,
                active_label="Error descargando Base",
                percent_override=70,
                note="La copia de VoiceDesign, si ya se descargo, seguira disponible localmente.",
            ),
            f"Error al descargar Base: {exc}",
        )
        return

    final_settings = tts_service.get_settings_summary()
    final_message = "Modelos descargados y listos para reutilizar localmente."
    yield (
        render_settings_snapshot_html(final_settings),
        render_storage_snapshot_html(final_settings),
        render_runtime_snapshot_html(base_status),
        render_model_progress_html(
            base_status,
            active_label="Proceso finalizado",
            percent_override=100,
            note=final_message,
        ),
        f"{final_message} {base_message}",
    )
