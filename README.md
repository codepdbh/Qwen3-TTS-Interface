# Qwen3 TTS Studio

Aplicacion local para Windows 10/11 hecha en Python + Gradio para trabajar con Qwen3-TTS en CPU. La interfaz abre en el navegador local y organiza el trabajo en cinco pestanas: diseno de voz, clonacion, flujo hibrido, historial y configuracion.

## Que hace la app

- Genera TTS por descripcion de voz con `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`.
- Clona voz desde un audio de referencia con `Qwen/Qwen3-TTS-12Hz-1.7B-Base`.
- Ejecuta el flujo hibrido "Voice Design then Clone".
- Permite subir audio de referencia y transcripcion opcional.
- Reproduce el audio generado y ofrece descarga del WAV.
- Guarda un historial local en JSON.
- Permite guardar voces reutilizables desde audio de referencia o desde una semilla híbrida.
- Muestra configuracion y estado de modelos cargados.
- Descarga y conserva copias locales persistentes de los modelos.

## Requisitos

- Windows 10 u 11
- Python 3.12 recomendado
- PowerShell
- Conexion a internet para descargar modelos desde Hugging Face en la primera carga
- Memoria RAM suficiente para ejecutar modelos de 1.7B en CPU

## Instalacion paso a paso en Windows

Abre PowerShell dentro de la carpeta `qwen3_tts_studio` y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Como ejecutar la app

Con el entorno activado:

```powershell
python app.py
```

La app se iniciara en:

```text
http://127.0.0.1:7860
```

Si cambias el puerto en `config/settings.json`, la aplicacion usara ese valor en el siguiente arranque.

## Descarga persistente de modelos

La app guarda los modelos en carpetas locales del proyecto:

- `models/voice_design`
- `models/base`

Comportamiento:

- La primera vez que uses un modo, si el modelo local no existe, la app lo descarga automaticamente.
- En la pestana `Configuracion` tambien puedes usar `Descargar modelos`.
- En siguientes arranques la app intenta cargar desde esas carpetas locales primero.
- Eso evita tener que volver a bajar el modelo completo cada vez que abras la aplicacion.

## Como usar cada pestana

### 1. Diseno de voz

- Escribe el texto a sintetizar.
- Selecciona el idioma.
- Describe la voz deseada.
- Usa un ejemplo rapido si quieres.
- Pulsa `Generar`.

Este modo usa `VoiceDesign`, pensado para crear una voz desde una descripcion textual.

### 2. Clonacion de voz

- Escribe el texto objetivo.
- Selecciona el idioma.
- Elige entre subir un audio nuevo o usar una voz guardada.
- Si conoces la transcripcion del audio, escribela.
- Si subes un audio nuevo, puedes guardarlo como voz reusable.
- Pulsa `Clonar voz`.

Si no proporcionas transcripcion, la app usa `x_vector_only_mode=True`. Eso permite clonar solo con el audio, aunque la calidad puede ser menor que con transcripcion.

### 3. Diseno + Clonacion

- Escribe el texto final.
- Selecciona el idioma.
- Describe la voz.
- Opcionalmente ajusta el texto semilla.
- Pulsa `Generar con flujo hibrido`.
- Si te gusta la semilla generada, puedes guardarla como voz reusable.

Este modo:

- Genera primero un clip semilla con `VoiceDesign`.
- Usa esa semilla para crear un prompt reutilizable de clonacion con `Base`.
- Produce el audio final con el texto objetivo.

### 4. Voces guardadas

- Muestra la biblioteca local de voces guardadas.
- Permite previsualizar cada voz.
- Permite borrar voces que ya no necesites.

### 5. Historial

- Muestra registros previos en una tabla.
- Permite refrescar.
- Permite borrar un item.
- Permite limpiar todo el historial.
- Si el archivo sigue existiendo, puedes reproducirlo desde la propia pestana.

### 6. Configuracion

- Muestra dispositivo, puerto y rutas.
- Muestra el estado de modelos cargados.
- Permite recargar `settings.json`.
- Permite descargar modelos de memoria.
- Permite descargar o actualizar las copias locales de los modelos.

## Archivo de configuracion

El archivo principal es `config/settings.json`.

Ejemplo:

```json
{
  "app_name": "Qwen3 TTS Studio",
  "host": "127.0.0.1",
  "port": 7860,
  "device": "cpu",
  "output_dir": "outputs/generated",
  "history_file": "outputs/history/history.json",
  "temp_dir": "outputs/temp",
  "voices_dir": "outputs/voices",
  "voices_file": "outputs/voices/voices.json",
  "models_dir": "models",
  "voice_design_local_dir": "models/voice_design",
  "base_local_dir": "models/base",
  "download_models_on_demand": true,
  "default_language": "Spanish",
  "voice_design_model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
  "base_model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
  "share": false,
  "debug": true
}
```

## Limitaciones de usar CPU

- La primera carga del modelo puede tardar varios minutos.
- La inferencia sera significativamente mas lenta que en GPU.
- Los modelos de 1.7B pueden exigir bastante RAM.
- En equipos modestos puede ser necesario descargar modelos de memoria entre tareas.
- No se usa FlashAttention ni optimizaciones CUDA.

## Errores comunes

### 1. Error al descargar el modelo

Posibles causas:

- Sin conexion a internet.
- Restricciones de red hacia Hugging Face.
- Poco espacio en disco o caché corrupta.

Que revisar:

- Prueba acceder a Hugging Face desde el navegador.
- Reintenta despues de cerrar la app.
- Limpia la cache si sospechas una descarga rota.

### 2. `qwen_tts` no se pudo importar

Posibles causas:

- Dependencias incompletas.
- Version de Python no compatible con tu instalacion.

Que revisar:

- Usa Python 3.12.
- Ejecuta `pip install -r requirements.txt` dentro del entorno virtual.

### 3. El audio de referencia no se encuentra

Posibles causas:

- El archivo temporal de Gradio ya no existe.
- Se selecciono un archivo y luego se borro o movio.

Que revisar:

- Vuelve a subir el audio.
- Usa formatos comunes como `.wav`, `.mp3`, `.m4a`, `.flac` u `.ogg`.

### 4. La clonacion sin transcripcion suena peor

Esto es esperado en algunos casos. Cuando no hay transcripcion, la app usa solo la huella de locutor (`x_vector_only_mode=True`). Para resultados mas estables, conviene incluir la transcripcion manual si la conoces.

## Estructura del proyecto

```text
qwen3_tts_studio/
  app.py
  requirements.txt
  README.md
  .gitignore
  config/
    settings.json
  models/
    voice_design/
    base/
  core/
    __init__.py
    device.py
    model_manager.py
    audio_utils.py
    history_manager.py
    validators.py
    constants.py
  services/
    __init__.py
    tts_service.py
    clone_service.py
    design_service.py
    hybrid_service.py
  ui/
    __init__.py
    tabs_generate.py
    tabs_clone.py
    tabs_hybrid.py
    tabs_history.py
    tabs_settings.py
    components.py
  outputs/
    generated/
    history/
    temp/
    voices/
  assets/
    app.css
```

## Detalles de implementacion

- Carga diferida de modelos: no carga todos los modelos al inicio.
- Descarga persistente con `huggingface_hub` a carpetas locales del proyecto.
- Device por defecto: CPU.
- Historial en JSON local.
- Rutas gestionadas con `pathlib`.
- Manejo de errores con mensajes amigables en UI y traceback en consola.
- Cola de Gradio limitada a una solicitud concurrente para evitar sobrecarga en CPU.

## Ajustes posibles segun la version de qwen-tts

La integracion esta encapsulada en `core/model_manager.py` y los servicios de `services/`. Si la API exacta de `qwen-tts` cambia en una version futura, normalmente bastara con ajustar:

- Las opciones de `from_pretrained(...)`
- Los argumentos de `generate_voice_design(...)`
- Los argumentos de `generate_voice_clone(...)`
- La construccion de `voice_clone_prompt`

## Ideas para futuras mejoras

- Integrar ASR con Whisper para rellenar la transcripcion automaticamente
- Guardar presets de voz
- Exportar a MP3
- Implementar cola de tareas
- Añadir modo batch
- Guardar voces favoritas o perfiles reutilizables
- Añadir soporte CUDA cuando se quiera usar GPU NVIDIA

## Notas finales

- `VoiceDesign` disena una voz desde texto descriptivo.
- `Base` permite clonacion desde audio.
- El modo hibrido combina ambos.
- En CPU el tiempo de generacion puede ser alto.
- Audios de referencia limpios dan mejores resultados.
