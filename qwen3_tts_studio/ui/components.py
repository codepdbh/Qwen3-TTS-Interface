from typing import Any


def info_box_markdown(title: str, body: str) -> str:
    return f"### {title}\n\n{body}"


def app_header_html() -> str:
    return """
<section class="hero-banner">
  <div class="hero-copy">
    <div class="hero-kicker">Qwen3 TTS Studio</div>
    <h1>Estudio local para disenar, clonar y refinar voces con Qwen3-TTS</h1>
    <p>Interfaz en espanol, pensada para Windows 10/11 y ejecucion en CPU. La primera carga puede tardar, pero despues puedes reutilizar modelos y audios generados desde una sola app.</p>
    <div class="hero-chips">
      <span>VoiceDesign</span>
      <span>Base</span>
      <span>Flujo hibrido</span>
      <span>Historial local</span>
    </div>
  </div>
  <div class="hero-grid">
    <div class="hero-card">
      <div class="hero-card-title">Diseno de voz</div>
      <p>Crea una identidad vocal a partir de una descripcion textual.</p>
    </div>
    <div class="hero-card">
      <div class="hero-card-title">Clonacion</div>
      <p>Usa un audio de referencia y, si quieres, su transcripcion.</p>
    </div>
    <div class="hero-card">
      <div class="hero-card-title">CPU primero</div>
      <p>Carga diferida de modelos y uso local sin depender de GPU NVIDIA.</p>
    </div>
  </div>
</section>
"""


def tab_header_html(kicker: str, title: str, description: str) -> str:
    return f"""
<section class="tab-intro-card">
  <div class="tab-intro-kicker">{kicker}</div>
  <h2>{title}</h2>
  <p>{description}</p>
</section>
"""


def tips_card_html(title: str, items: list[str]) -> str:
    list_items = "".join(f"<li>{item}</li>" for item in items)
    return f"""
<section class="tips-card">
  <div class="tips-card-title">{title}</div>
  <ul>{list_items}</ul>
</section>
"""


def footer_notes_html() -> str:
    return """
<section class="footer-notes">
  <div class="footer-note">
    <div class="footer-note-title">VoiceDesign</div>
    <p>Disena una voz desde una descripcion textual.</p>
  </div>
  <div class="footer-note">
    <div class="footer-note-title">Base</div>
    <p>Clona una voz a partir de un audio limpio de referencia.</p>
  </div>
  <div class="footer-note">
    <div class="footer-note-title">Modo hibrido</div>
    <p>Genera una voz semilla y la convierte en prompt reutilizable.</p>
  </div>
  <div class="footer-note">
    <div class="footer-note-title">CPU</div>
    <p>La generacion puede tardar bastante; los modelos se cargan solo cuando hacen falta.</p>
  </div>
</section>
"""


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
