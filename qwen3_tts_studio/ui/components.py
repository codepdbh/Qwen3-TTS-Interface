from typing import Any


def info_box_markdown(title: str, body: str) -> str:
    return f"### {title}\n\n{body}"


def build_history_selector_label(record: dict[str, Any]) -> str:
    return f"{record.get('id', '')} | {record.get('fecha_hora', '')} | {record.get('modo', '')}"


def parse_history_selector_label(value: str | None) -> str | None:
    if not value:
        return None
    return value.split(" | ", 1)[0].strip() or None


def history_detail_markdown(record: dict[str, Any] | None) -> str:
    if not record:
        return "Selecciona un registro para ver su detalle."

    lines = [
        "### Detalle del registro",
        f"- ID: `{record.get('id', '')}`",
        f"- Fecha: `{record.get('fecha_hora', '')}`",
        f"- Modo: `{record.get('modo', '')}`",
        f"- Idioma: `{record.get('idioma', '')}`",
        f"- Estado: `{record.get('estado', '')}`",
        f"- Modelo: `{record.get('modelo_usado', '') or 'N/D'}`",
        f"- Salida: `{record.get('archivo_salida_generado', '') or 'N/D'}`",
    ]
    if record.get("archivo_semilla"):
        lines.append(f"- Semilla: `{record.get('archivo_semilla')}`")
    if record.get("archivo_referencia"):
        lines.append(f"- Referencia: `{record.get('archivo_referencia')}`")
    if record.get("descripcion_de_voz"):
        lines.append(f"- Descripcion de voz: `{record.get('descripcion_de_voz')}`")
    if record.get("mensaje_error"):
        lines.append(f"- Error: `{record.get('mensaje_error')}`")
    lines.append("")
    lines.append(record.get("texto", ""))
    return "\n".join(lines)


def render_model_progress_html(
    model_status: dict[str, Any] | None,
    active_label: str | None = None,
    percent_override: int | None = None,
    note: str | None = None,
) -> str:
    status = model_status or {}
    voice_downloaded = bool(status.get("voice_design_downloaded"))
    base_downloaded = bool(status.get("base_downloaded"))
    downloaded_count = int(voice_downloaded) + int(base_downloaded)
    percent = percent_override if percent_override is not None else int((downloaded_count / 2) * 100)
    active_text = active_label or "Sin descarga en curso"
    note_text = note or "La app reutiliza estas carpetas locales en futuros arranques."

    cards = [
        _render_model_card(
            title="VoiceDesign",
            downloaded=voice_downloaded,
            loaded=bool(status.get("voice_design_loaded")),
            path=status.get("voice_design_local_dir", ""),
        ),
        _render_model_card(
            title="Base",
            downloaded=base_downloaded,
            loaded=bool(status.get("base_loaded")),
            path=status.get("base_local_dir", ""),
        ),
    ]

    return f"""
<div class="model-progress-panel">
  <div class="model-progress-header">
    <div>
      <div class="model-progress-title">Estado de modelos locales</div>
      <div class="model-progress-subtitle">{downloaded_count}/2 modelos descargados</div>
    </div>
    <div class="model-progress-badge">{percent}%</div>
  </div>
  <div class="model-progress-track">
    <div class="model-progress-fill" style="width: {max(0, min(percent, 100))}%;"></div>
  </div>
  <div class="model-progress-note"><strong>Actividad:</strong> {active_text}</div>
  <div class="model-progress-grid">
    {''.join(cards)}
  </div>
  <div class="model-progress-footnote">{note_text}</div>
</div>
"""


def _render_model_card(title: str, downloaded: bool, loaded: bool, path: str) -> str:
    downloaded_text = "Descargado" if downloaded else "Pendiente"
    loaded_text = "Cargado en memoria" if loaded else "No cargado"
    badge_class = "ok" if downloaded else "pending"
    load_class = "ok" if loaded else "pending"
    return f"""
<div class="model-status-card">
  <div class="model-status-row">
    <span class="model-status-name">{title}</span>
    <span class="model-status-chip {badge_class}">{downloaded_text}</span>
  </div>
  <div class="model-status-subrow">
    <span class="model-status-chip small {load_class}">{loaded_text}</span>
  </div>
  <div class="model-status-path">{path}</div>
</div>
"""
