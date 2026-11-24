"""Monitoreo de la herramienta final (paquetes 2.6.3 y 2.6.4).

- RF.11: compara la segmentación nueva con la anterior y dice cuántos clientes cambiaron de segmento.
- RF.12: avisa cuando los datos de entrada cambian mucho respecto de la base anterior (deriva).
- RNF.12: deja un registro de cada ejecución, para saber cuánto se usa la herramienta.
"""
from __future__ import annotations

import csv
from datetime import datetime

import numpy as np
import pandas as pd

from . import config


def psi(anterior, nueva, tramos: int = 10) -> float:
    """Índice de estabilidad poblacional entre dos muestras de una variable numérica.
    Menos de 0,10 es estable; entre 0,10 y 0,20, cambio moderado; sobre 0,20, deriva."""
    anterior, nueva = np.asarray(anterior, float), np.asarray(nueva, float)
    cortes = np.unique(np.quantile(anterior, np.linspace(0, 1, tramos + 1)))
    cortes[0], cortes[-1] = -np.inf, np.inf
    p = np.histogram(anterior, cortes)[0] / len(anterior)
    q = np.histogram(nueva, cortes)[0] / len(nueva)
    p, q = np.clip(p, 1e-4, None), np.clip(q, 1e-4, None)
    return float(np.sum((q - p) * np.log(q / p)))


def alerta_deriva(base_anterior: pd.DataFrame, base_nueva: pd.DataFrame,
                  variables=config.VARIABLES_MODELO) -> pd.DataFrame:
    """Una fila por variable del modelo con su PSI y si corresponde avisar (RF.12)."""
    filas = [{"variable": v, "psi": round(psi(base_anterior[v], base_nueva[v]), 3)} for v in variables]
    tabla = pd.DataFrame(filas)
    tabla["alerta"] = tabla["psi"] > config.PSI_ALERTA
    return tabla


def comparar_segmentaciones(anterior: pd.DataFrame, nueva: pd.DataFrame) -> dict:
    """Compara por seudónimo el nombre del segmento anterior y el nuevo (RF.11)."""
    a = anterior[["seudonimo", "nombre_segmento"]].rename(columns={"nombre_segmento": "anterior"})
    n = nueva[["seudonimo", "nombre_segmento"]].rename(columns={"nombre_segmento": "nuevo"})
    cruce = a.merge(n, on="seudonimo", how="inner")
    cambiaron = cruce["anterior"] != cruce["nuevo"]
    return {
        "clientes_comparados": len(cruce),
        "cambiaron": int(cambiaron.sum()),
        "pct_cambiaron": round(float(cambiaron.mean() * 100), 1) if len(cruce) else 0.0,
        "matriz": pd.crosstab(cruce["anterior"], cruce["nuevo"]),
    }


def registrar_ejecucion(version: str, archivo: str, k: int, clientes: int, alertas: int,
                        ruta=config.REGISTRO_EJECUCIONES) -> None:
    """Agrega una línea al registro de ejecuciones (RNF.12). No guarda datos de clientes."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    nueva = not ruta.exists()
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nueva:
            w.writerow(["fecha", "version", "archivo", "segmentos", "clientes", "alertas_deriva"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), version, archivo, k, clientes, alertas])


def resumen_uso(ruta=config.REGISTRO_EJECUCIONES) -> dict:
    """Cuántas segmentaciones se hicieron y cuándo fue la última (indicador de RNF.12)."""
    if not ruta.exists():
        return {"ejecuciones": 0, "ultima": None}
    reg = pd.read_csv(ruta)
    return {"ejecuciones": len(reg), "ultima": reg["fecha"].iloc[-1]}
