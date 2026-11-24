"""Modelos de clustering (paquetes 2.4.1 a 2.4.3)."""
import numpy as np
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans

from . import config


def kmeans(X, k: int, semilla: int = config.SEMILLA) -> KMeans:
    return KMeans(n_clusters=k, n_init=20, random_state=semilla).fit(X)


def jerarquico(X, k: int) -> np.ndarray:
    return AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(X)


def dbscan(X, eps: float, min_muestras: int = 5) -> np.ndarray:
    """Devuelve etiquetas; -1 es ruido (clientes que no quedan en ningún segmento)."""
    return DBSCAN(eps=eps, min_samples=min_muestras).fit_predict(X)


def ordenar_etiquetas(etiquetas: np.ndarray, valores: np.ndarray) -> np.ndarray:
    """Renumera los segmentos de 1 a k según el índice de gasto medio, para que el
    número de cada segmento sea estable entre corridas y legible para Marketing."""
    unicos = [e for e in np.unique(etiquetas) if e != -1]
    medias = {e: valores[etiquetas == e].mean() for e in unicos}
    orden = sorted(unicos, key=lambda e: medias[e], reverse=True)
    mapa = {e: i + 1 for i, e in enumerate(orden)}
    mapa[-1] = 0
    return np.array([mapa[e] for e in etiquetas])
