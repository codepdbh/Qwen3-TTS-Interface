import json
from pathlib import Path
from typing import Any

from core.audio_utils import ensure_directory


class HistoryManager:
    def __init__(self, history_file: str | Path) -> None:
        self.history_file = Path(history_file)
        ensure_directory(self.history_file.parent)
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")

    def update_history_file(self, history_file: str | Path) -> None:
        self.history_file = Path(history_file)
        ensure_directory(self.history_file.parent)
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")

    def load_history(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:
            data = []
        if not isinstance(data, list):
            return []
        return data

    def save_history(self, records: list[dict[str, Any]]) -> None:
        self.history_file.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_history_record(self, record: dict[str, Any]) -> None:
        records = self.load_history()
        records.insert(0, record)
        self.save_history(records)

    def get_history_dataframe_like(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for item in self.load_history():
            output_path = item.get("archivo_salida_generado") or ""
            rows.append(
                [
                    item.get("id", ""),
                    item.get("fecha_hora", ""),
                    item.get("modo", ""),
                    self._short_text(item.get("texto", "")),
                    output_path,
                    item.get("estado", ""),
                ]
            )
        return rows

    def get_record(self, record_id: str) -> dict[str, Any] | None:
        for item in self.load_history():
            if item.get("id") == record_id:
                return item
        return None

    def delete_history_item(self, record_id: str) -> bool:
        records = self.load_history()
        filtered = [item for item in records if item.get("id") != record_id]
        changed = len(filtered) != len(records)
        if changed:
            self.save_history(filtered)
        return changed

    def clear_history(self) -> None:
        self.save_history([])

    @staticmethod
    def _short_text(text: str, limit: int = 70) -> str:
        clean = (text or "").strip().replace("\n", " ")
        if len(clean) <= limit:
            return clean
        return f"{clean[: limit - 3]}..."

