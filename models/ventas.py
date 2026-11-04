"""Persistencia local de las ventas, sin guardar datos personales del cliente."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from models.producto import Producto


class RegistroVentas:
    """Guarda un historial sencillo de ventas para el panel administrativo."""

    def __init__(self, archivo_json: str | None = None):
        self.archivo_json = (
            Path(archivo_json)
            if archivo_json
            else Path(__file__).resolve().parent.parent / "data" / "ventas.json"
        )
        self.archivo_json.parent.mkdir(parents=True, exist_ok=True)

    def listar(self) -> list[dict]:
        if not self.archivo_json.exists():
            return []

        try:
            with self.archivo_json.open("r", encoding="utf-8") as archivo:
                ventas = json.load(archivo)
        except (json.JSONDecodeError, OSError) as exc:
            raise OSError("No se pudo leer el historial de ventas.") from exc

        if not isinstance(ventas, list):
            raise ValueError("El historial de ventas debe contener una lista.")
        return ventas

    def registrar(self, producto: Producto, cantidad: int, precio_unitario: float) -> dict:
        ventas = self.listar()
        venta = {
            "id": max((item.get("id", 0) for item in ventas), default=0) + 1,
            "producto_id": producto.id,
            "producto": producto.nombre,
            "cantidad": cantidad,
            "precio_unitario": round(precio_unitario, 2),
            "total": round(precio_unitario * cantidad, 2),
            "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        ventas.insert(0, venta)

        archivo_temporal = self.archivo_json.with_suffix(".tmp")
        try:
            with archivo_temporal.open("w", encoding="utf-8") as archivo:
                json.dump(ventas, archivo, ensure_ascii=False, indent=2)
            archivo_temporal.replace(self.archivo_json)
        except OSError:
            if archivo_temporal.exists():
                archivo_temporal.unlink()
            raise
        return venta
