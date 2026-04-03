#!/usr/bin/env python3
"""Sistema de gestión para emprendimientos.

Funcionalidades:
- Registrar ventas
- Registrar gastos
- Ver ganancias
- Exportar reportes

Los datos se guardan localmente en JSON para que persistan entre ejecuciones.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List

DATA_FILE = Path("datos_emprendimiento.json")


@dataclass
class Movimiento:
    tipo: str  # "venta" o "gasto"
    descripcion: str
    monto: float
    fecha: str  # ISO YYYY-MM-DD


class SistemaEmprendimiento:
    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self.data_file = data_file
        self.movimientos: List[Movimiento] = []
        self.cargar_datos()

    def cargar_datos(self) -> None:
        if not self.data_file.exists():
            self.movimientos = []
            return

        with self.data_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.movimientos = [Movimiento(**item) for item in data]

    def guardar_datos(self) -> None:
        data = [asdict(m) for m in self.movimientos]
        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def registrar_venta(self, descripcion: str, monto: float, fecha: str | None = None) -> None:
        self._registrar_movimiento("venta", descripcion, monto, fecha)

    def registrar_gasto(self, descripcion: str, monto: float, fecha: str | None = None) -> None:
        self._registrar_movimiento("gasto", descripcion, monto, fecha)

    def _registrar_movimiento(self, tipo: str, descripcion: str, monto: float, fecha: str | None) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que 0.")

        fecha_final = fecha or datetime.now().strftime("%Y-%m-%d")
        self.movimientos.append(
            Movimiento(tipo=tipo, descripcion=descripcion.strip(), monto=round(monto, 2), fecha=fecha_final)
        )
        self.guardar_datos()

    def resumen(self) -> dict:
        total_ventas = round(sum(m.monto for m in self.movimientos if m.tipo == "venta"), 2)
        total_gastos = round(sum(m.monto for m in self.movimientos if m.tipo == "gasto"), 2)
        ganancia = round(total_ventas - total_gastos, 2)

        return {
            "total_ventas": total_ventas,
            "total_gastos": total_gastos,
            "ganancia": ganancia,
            "cantidad_movimientos": len(self.movimientos),
        }

    def exportar_csv(self, ruta_salida: Path = Path("reporte_emprendimiento.csv")) -> Path:
        with ruta_salida.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["tipo", "descripcion", "monto", "fecha"])
            for m in self.movimientos:
                writer.writerow([m.tipo, m.descripcion, f"{m.monto:.2f}", m.fecha])
        return ruta_salida


def pedir_texto(mensaje: str) -> str:
    valor = input(mensaje).strip()
    if not valor:
        raise ValueError("No puede estar vacío.")
    return valor


def pedir_monto(mensaje: str) -> float:
    valor = input(mensaje).strip().replace(",", ".")
    monto = float(valor)
    if monto <= 0:
        raise ValueError
    return monto


def mostrar_menu() -> None:
    print("\n=== SISTEMA DE GESTIÓN PARA EMPRENDIMIENTOS ===")
    print("1) Registrar venta")
    print("2) Registrar gasto")
    print("3) Ver ganancias (resumen)")
    print("4) Exportar reporte CSV")
    print("5) Salir")


def main() -> None:
    sistema = SistemaEmprendimiento()

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        try:
            if opcion == "1":
                descripcion = pedir_texto("Descripción de la venta: ")
                monto = pedir_monto("Monto de la venta: ")
                sistema.registrar_venta(descripcion, monto)
                print("✅ Venta registrada.")

            elif opcion == "2":
                descripcion = pedir_texto("Descripción del gasto: ")
                monto = pedir_monto("Monto del gasto: ")
                sistema.registrar_gasto(descripcion, monto)
                print("✅ Gasto registrado.")

            elif opcion == "3":
                r = sistema.resumen()
                print("\n--- RESUMEN ---")
                print(f"Ventas totales : ${r['total_ventas']:.2f}")
                print(f"Gastos totales : ${r['total_gastos']:.2f}")
                print(f"Ganancia neta  : ${r['ganancia']:.2f}")
                print(f"Movimientos    : {r['cantidad_movimientos']}")

            elif opcion == "4":
                ruta = sistema.exportar_csv()
                print(f"✅ Reporte exportado en: {ruta.resolve()}")

            elif opcion == "5":
                print("Hasta luego 👋")
                break

            else:
                print("Opción no válida. Elige 1-5.")

        except ValueError:
            print("⚠️ Entrada inválida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
