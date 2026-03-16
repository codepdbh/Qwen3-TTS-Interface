import html
from typing import Any


def info_box_markdown(title: str, body: str) -> str:
    return f"### {title}\n\n{body}"


def app_header_html() -> str:
    return """
<section class="app-hero">
  <div class="app-hero-copy">
    <div class="app-eyebrow">Qwen3 TTS Studio</div>
    <h1>Disena, clona y organiza voces desde una sola interfaz</h1>
    <p>Aplicacion local en espanol para Windows 10/11. Pensada para trabajo en CPU, con carga diferida de modelos, historial local y biblioteca de voces reutilizables.</p>
    <div class="app-pill-row">
      <span>VoiceDesign</span>
      <span>Base</span>
      <span>Flujo hibrido</span>
      <span>Voces guardadas</span>
    </div>
  </div>
  <div class="app-hero-side">
    <div class="hero-side-card">
      <div class="hero-side-kicker">Como se usa</div>
      <h3>Un flujo claro</h3>
      <p>Elige un modo, completa los pasos guiados y revisa el resultado en el panel lateral. Las acciones secundarias quedan agrupadas para no estorbar.</p>
    </div>
    <div class="hero-side-grid">
      <div class="hero-metric">
        <strong>3</strong>
        <span>modos de sintesis</span>
      </div>
      <div class="hero-metric">
        <strong>CPU</strong>
        <span>sin GPU NVIDIA</span>
      </div>
      <div class="hero-metric">
        <strong>Local</strong>
        <span>historial y voces</span>
      </div>
      <div class="hero-metric">
        <strong>WAV</strong>
        <span>salida descargable</span>
      </div>
    </div>
  </div>
</section>
<section class="mode-strip">
  <article class="mode-tile">
    <div class="mode-tile-label">Diseno de voz</div>
    <p>Crea una identidad vocal desde una descripcion textual.</p>
  </article>
  <article class="mode-tile">
    <div class="mode-tile-label">Clonacion</div>
    <p>Usa un audio nuevo o una voz guardada como referencia.</p>
  </article>
  <article class="mode-tile">
    <div class="mode-tile-label">Diseno + clonacion</div>
    <p>Genera una semilla y conviertela en una voz reutilizable.</p>
  </article>
  <article class="mode-tile mode-tile-warning">
    <div class="mode-tile-label">Rendimiento</div>
    <p>En CPU la primera carga y algunas sintesis pueden tardar bastante.</p>
  </article>
</section>
"""


def tab_header_html(kicker: str, title: str, description: str) -> str:
    return f"""
<section class="tab-banner">
  <div class="tab-banner-kicker">{html.escape(kicker)}</div>
  <div class="tab-banner-content">
    <h2>{html.escape(title)}</h2>
    <p>{html.escape(description)}</p>
  </div>
</section>
"""


def step_header_html(number: int, title: str, description: str) -> str:
    return f"""
<div class="step-header">
  <div class="step-badge">{number}</div>
  <div class="step-copy">
    <div class="step-title">{html.escape(title)}</div>
    <div class="step-description">{html.escape(description)}</div>
  </div>
</div>
"""


def tips_card_html(title: str, items: list[str], tone: str = "default") -> str:
    list_items = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f"""
<section class="tips-card tips-card-{html.escape(tone)}">
  <div class="tips-card-title">{html.escape(title)}</div>
  <ul>{list_items}</ul>
</section>
"""


def text_card_html(title: str, body: str, tone: str = "default") -> str:
    return f"""
<section class="text-card text-card-{html.escape(tone)}">
  <div class="text-card-title">{html.escape(title)}</div>
  <p>{html.escape(body)}</p>
</section>
"""


def render_settings_snapshot_html(settings: dict[str, Any]) -> str:
    return _kv_card_html(
        "Configuracion activa",
        [
            ("Aplicacion", settings.get("app_name", "")),
            ("Host", settings.get("host", "")),
            ("Puerto", settings.get("port", "")),
            ("Dispositivo", settings.get("device", "")),
            ("Compartir", "si" if settings.get("share") else "no"),
            ("Debug", "si" if settings.get("debug") else "no"),
            ("Idioma por defecto", settings.get("default_language", "Spanish")),
        ],
    )


def render_storage_snapshot_html(settings: dict[str, Any]) -> str:
    return _kv_card_html(
        "Rutas de trabajo",
        [
            ("Generados", settings.get("output_dir", "")),
            ("Historial", settings.get("history_file", "")),
            ("Temporales", settings.get("temp_dir", "")),
            ("Biblioteca de voces", settings.get("voices_dir", "")),
            ("Archivo de voces", settings.get("voices_file", "")),
            ("Modelos locales", settings.get("models_dir", "")),
        ],
    )


def render_runtime_snapshot_html(status: dict[str, Any]) -> str:
    return _kv_card_html(
        "Estado de ejecucion",
        [
            ("VoiceDesign descargado", "si" if status.get("voice_design_downloaded") else "no"),
            ("VoiceDesign cargado", "si" if status.get("voice_design_loaded") else "no"),
            ("Base descargado", "si" if status.get("base_downloaded") else "no"),
            ("Base cargado", "si" if status.get("base_loaded") else "no"),
            ("Descarga bajo demanda", "si" if status.get("download_models_on_demand") else "no"),
        ],
    )


def build_history_selector_label(record: dict[str, Any]) -> str:
    return f"{record.get('id', '')} | {record.get('fecha_hora', '')} | {record.get('modo', '')}"


def parse_history_selector_label(value: str | None) -> str | None:
    if not value:
        return None
    return value.split(" | ", 1)[0].strip() or None


def build_voice_selector_label(record: dict[str, Any]) -> str:
    return f"{record.get('id', '')} | {record.get('name', '')} | {record.get('source_mode', '')}"


def parse_voice_selector_label(value: str | None) -> str | None:
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


def saved_voice_detail_markdown(record: dict[str, Any] | None) -> str:
    if not record:
        return "Selecciona una voz guardada para ver su detalle."

    lines = [
        "### Voz guardada",
        f"- ID: `{record.get('id', '')}`",
        f"- Nombre: `{record.get('name', '')}`",
        f"- Creada: `{record.get('created_at', '')}`",
        f"- Origen: `{record.get('source_mode', '')}`",
        f"- Idioma: `{record.get('language', '') or 'N/D'}`",
        f"- Audio: `{record.get('audio_path', '')}`",
        f"- Tiene transcripcion: `{'si' if record.get('reference_text') else 'no'}`",
    ]
    if record.get("reference_text"):
        lines.append(f"- Transcripcion: `{record.get('reference_text')}`")
    if record.get("voice_prompt"):
        lines.append(f"- Prompt de voz: `{record.get('voice_prompt')}`")
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
<section class="progress-shell">
  <div class="progress-shell-top">
    <div>
      <div class="progress-shell-title">Estado de modelos locales</div>
      <div class="progress-shell-subtitle">{downloaded_count}/2 modelos disponibles</div>
    </div>
    <div class="progress-pill">{percent}%</div>
  </div>
  <div class="progress-track">
    <div class="progress-fill" style="width: {max(0, min(percent, 100))}%;"></div>
  </div>
  <div class="progress-activity"><strong>Actividad:</strong> {html.escape(active_text)}</div>
  <div class="progress-grid">
    {''.join(cards)}
  </div>
  <div class="progress-note">{html.escape(note_text)}</div>
</section>
"""


def _render_model_card(title: str, downloaded: bool, loaded: bool, path: str) -> str:
    downloaded_text = "Descargado" if downloaded else "Pendiente"
    loaded_text = "Cargado" if loaded else "No cargado"
    badge_class = "ok" if downloaded else "pending"
    load_class = "ok" if loaded else "pending"
    return f"""
<article class="progress-card">
  <div class="progress-card-top">
    <span class="progress-card-name">{html.escape(title)}</span>
    <span class="status-chip status-chip-{badge_class}">{downloaded_text}</span>
  </div>
  <div class="progress-card-mid">
    <span class="status-chip status-chip-{load_class}">{loaded_text}</span>
  </div>
  <div class="progress-card-path">{html.escape(path)}</div>
</article>
"""


def _kv_card_html(title: str, rows: list[tuple[str, Any]]) -> str:
    items = "".join(
        f"""
<div class="kv-row">
  <div class="kv-key">{html.escape(str(key))}</div>
  <div class="kv-value">{html.escape(str(value))}</div>
</div>
"""
        for key, value in rows
    )
    return f"""
<section class="kv-card">
  <div class="kv-card-title">{html.escape(title)}</div>
  <div class="kv-grid">
    {items}
  </div>
</section>
"""
