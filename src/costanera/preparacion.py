"""Preparación de la base analítica (paquetes 2.3.1 a 2.3.3, RNF.4).

- Seudonimiza el identificador: el ambiente analítico no guarda el ID original.
- Agrega el tramo etario para revisar la composición de los segmentos.
- Filtra por consentimiento vigente cuando el archivo trae esa columna (2.3.2).
- Escala las variables del modelo.
"""
import hashlib
import os

import pandas as pd
from sklearn.preprocessing import StandardScaler

from . import config

# La sal se define fuera del código (variable de entorno) en producción; el valor por
# defecto solo sirve para que el ejercicio académico sea reproducible.
SAL = os.environ.get("COSTANERA_SAL", "sca-2026-01-academico")


def seudonimo(id_cliente) -> str:
    return hashlib.sha256(f"{SAL}:{id_cliente}".encode()).hexdigest()[:12]


def preparar(df: pd.DataFrame, solo_con_consentimiento: bool = False) -> pd.DataFrame:
    base = df.copy()
    if solo_con_consentimiento:
        if "consentimiento" not in base:
            raise ValueError("El archivo no trae la columna 'consentimiento'; no se puede hacer el corte 2.3.2.")
        base = base[base["consentimiento"].astype(bool)]
    base.insert(0, "seudonimo", base["id_cliente"].map(seudonimo))
    base["tramo_etario"] = pd.cut(base["edad"], bins=config.TRAMOS_EDAD,
                                  labels=config.ETIQUETAS_TRAMOS).astype(str)
    return base.drop(columns=["id_cliente"]).reset_index(drop=True)


def escalar(base: pd.DataFrame, variables=config.VARIABLES_MODELO):
    escalador = StandardScaler()
    X = escalador.fit_transform(base[variables])
    return X, escalador


def guardar_base(base: pd.DataFrame, version: str) -> str:
    """Guarda la base analítica versionada (sin identificadores directos)."""
    assert "id_cliente" not in base, "La base analítica no puede llevar el identificador original"
    config.DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
    ruta = config.DATOS_PROCESADOS / f"base_analitica_{version}.csv"
    base.to_csv(ruta, index=False)
    return str(ruta)
