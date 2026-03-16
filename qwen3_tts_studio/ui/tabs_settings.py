import gradio as gr

from ui.components import render_model_progress_html, tab_header_html, tips_card_html


def build_settings_tab(tts_service) -> None:
    def on_download_normal():
        yield from _download_models_generator(tts_service, force_download=False)

    def on_force_download():
        yield from _download_models_generator(tts_service, force_download=True)

    with gr.Tab("Configuracion"):
        gr.HTML(
            tab_header_html(
                "Entorno y modelos",
                "Configura, descarga y verifica el estado local",
                "Desde aqui puedes confirmar el dispositivo actual, revisar rutas y descargar copias persistentes de los modelos para no repetir la descarga en futuros arranques.",
            )
        )

        with gr.Row(elem_classes=["studio-workspace"]):
            with gr.Column(scale=1, elem_classes=["studio-panel", "studio-panel-side"]):
                progress_html = gr.HTML(
                    value=render_model_progress_html(
                        tts_service.get_model_status(),
                        note="Si descargas los modelos una vez, la app intentara reutilizar esas copias locales despues.",
                    )
                )
                gr.HTML(
                    tips_card_html(
                        "Que puedes hacer aqui",
                        [
                            "Descargar una copia local persistente de VoiceDesign y Base.",
                            "Actualizar el estado sin recargar toda la app.",
                            "Descargar modelos de memoria sin borrar los archivos del disco.",
                        ],
                    )
                )
                status_output = gr.Textbox(
                    label="Estado",
                    interactive=False,
                    value="Configuracion cargada. Puedes descargar los modelos una sola vez y quedaran guardados localmente.",
                )

                with gr.Row():
                    reload_button = gr.Button("Recargar configuracion", variant="secondary")
                    unload_button = gr.Button("Desalojar modelos", variant="secondary")
                    refresh_button = gr.Button("Actualizar estado", variant="primary")
                with gr.Row():
                    download_button = gr.Button("Descargar modelos", variant="primary")
                    force_download_button = gr.Button("Forzar actualizacion", variant="secondary")

            with gr.Column(scale=1, elem_classes=["studio-panel", "studio-panel-main"]):
                settings_json = gr.JSON(label="Configuracion actual", value=tts_service.get_settings_summary())
                model_status_json = gr.JSON(label="Estado de modelos", value=tts_service.get_model_status())

        reload_button.click(
            fn=lambda service=tts_service: _reload_settings(service),
            outputs=[settings_json, model_status_json, progress_html, status_output],
        )
        unload_button.click(
            fn=lambda service=tts_service: _unload_models(service),
            outputs=[settings_json, model_status_json, progress_html, status_output],
        )
        refresh_button.click(
            fn=lambda service=tts_service: _refresh_status(service),
            outputs=[settings_json, model_status_json, progress_html, status_output],
        )
        download_button.click(
            fn=on_download_normal,
            outputs=[settings_json, model_status_json, progress_html, status_output],
        )
        force_download_button.click(
            fn=on_force_download,
            outputs=[settings_json, model_status_json, progress_html, status_output],
        )


def _reload_settings(tts_service):
    settings = tts_service.reload_settings()
    model_status = tts_service.get_model_status()
    return (
        settings,
        model_status,
        render_model_progress_html(model_status),
        "Configuracion recargada desde settings.json.",
    )


def _unload_models(tts_service):
    model_status = tts_service.unload_models()
    return (
        tts_service.get_settings_summary(),
        model_status,
        render_model_progress_html(model_status, note="Los archivos siguen en disco aunque los modelos ya no esten cargados en memoria."),
        "Modelos descargados de memoria.",
    )


def _refresh_status(tts_service):
    model_status = tts_service.get_model_status()
    return tts_service.get_settings_summary(), model_status, render_model_progress_html(model_status), "Estado actualizado."


def _download_models_generator(tts_service, force_download: bool):
    mode_text = "forzada" if force_download else "normal"
    initial_status = tts_service.get_model_status()
    yield (
        tts_service.get_settings_summary(),
        initial_status,
        render_model_progress_html(
            initial_status,
            active_label=f"Preparando descarga {mode_text}",
            percent_override=5,
            note="Se descargara primero VoiceDesign y luego Base.",
        ),
        "Preparando descarga de modelos...",
    )

    yield (
        tts_service.get_settings_summary(),
        initial_status,
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
        failed_status = tts_service.get_model_status()
        yield (
            tts_service.get_settings_summary(),
            failed_status,
            render_model_progress_html(
                failed_status,
                active_label="Error descargando VoiceDesign",
                percent_override=15,
                note="Revisa la conexion a internet, espacio en disco o permisos.",
            ),
            f"Error al descargar VoiceDesign: {exc}",
        )
        return
    yield (
        tts_service.get_settings_summary(),
        voice_status,
        render_model_progress_html(
            voice_status,
            active_label="VoiceDesign descargado. Continuando con Base (2/2)",
            percent_override=55,
            note=voice_message,
        ),
        voice_message,
    )

    yield (
        tts_service.get_settings_summary(),
        voice_status,
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
        failed_status = tts_service.get_model_status()
        yield (
            tts_service.get_settings_summary(),
            failed_status,
            render_model_progress_html(
                failed_status,
                active_label="Error descargando Base",
                percent_override=70,
                note="La copia de VoiceDesign, si ya se descargo, seguira disponible localmente.",
            ),
            f"Error al descargar Base: {exc}",
        )
        return
    final_message = "Modelos descargados y listos para reutilizar localmente."
    yield (
        tts_service.get_settings_summary(),
        base_status,
        render_model_progress_html(
            base_status,
            active_label="Proceso finalizado",
            percent_override=100,
            note=final_message,
        ),
        f"{final_message} {base_message}",
    )
