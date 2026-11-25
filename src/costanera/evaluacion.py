"""Control técnico interno de cada evaluación (paquetes 2.5.1 a 2.5.3).

Tres chequeos de la iteración 1: silueta, tamaño mínimo de segmento y estabilidad entre
remuestreos. La brecha de composición por género y tramo etario (equidad) se incorpora en la
iteración 2, en la evaluación 2.5.2.
"""
from __future__ import annotations

import csv
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

from . import config


def silueta(X, etiquetas) -> float:
    m = etiquetas != -1 if np.any(etiquetas == -1) else np.ones(len(etiquetas), bool)
    if len(np.unique(etiquetas[m])) < 2:
        return float("nan")
    return float(silhouette_score(X[m], etiquetas[m]))


def tamano_minimo_pct(etiquetas) -> float:
    validas = etiquetas[etiquetas != -1]
    return float(np.bincount(validas - validas.min()).min() / len(etiquetas) * 100)


def estabilidad_kmeans(X, k: int, remuestreos: int = config.REMUESTREOS,
                       semilla: int = config.SEMILLA) -> float:
    """ARI medio entre el modelo completo y modelos entrenados con remuestreos bootstrap."""
    base = KMeans(n_clusters=k, n_init=20, random_state=semilla).fit(X)
    rng = np.random.default_rng(semilla)
    aris = []
    for b in range(remuestreos):
        idx = rng.choice(len(X), len(X), replace=True)
        m = KMeans(n_clusters=k, n_init=10, random_state=b).fit(X[idx])
        aris.append(adjusted_rand_score(base.labels_, m.predict(X)))
    return float(np.mean(aris))


def evaluar(X, etiquetas, base: pd.DataFrame | None = None, k: int | None = None,
            con_estabilidad: bool = True) -> dict:
    resultado = {
        "silueta": silueta(X, etiquetas),
        "tamano_min_pct": tamano_minimo_pct(etiquetas),
        "estabilidad": estabilidad_kmeans(X, k) if (con_estabilidad and k) else float("nan"),
        "ruido_pct": float(np.mean(etiquetas == -1) * 100),
    }
    return resultado


def veredicto(resultado: dict) -> dict:
    c = config.CRITERIOS
    chequeos = {
        "silueta >= 0,40": resultado["silueta"] >= c["silueta_min"],
        "ningún segmento < 5 %": resultado["tamano_min_pct"] >= c["tamano_min_pct"],
        "estabilidad >= 0,80": resultado["estabilidad"] >= c["estabilidad_min"],
    }
    return chequeos


def registrar_experimento(iteracion: str, algoritmo: str, parametros: str, variables,
                          resultado: dict, decision: str, ruta=config.REGISTRO_EXPERIMENTOS):
    """Agrega una fila al registro de experimentos (evidencia de RNF.11 y del paquete 2.4)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    nueva = not ruta.exists()
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nueva:
            w.writerow(["fecha_registro", "iteracion", "algoritmo", "parametros", "variables",
                        "silueta", "tamano_min_pct", "estabilidad", "ruido_pct", "decision"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), iteracion, algoritmo, parametros,
                    "+".join(variables), *(round(resultado[k], 3) for k in
                    ["silueta", "tamano_min_pct", "estabilidad", "ruido_pct"]), decision])
