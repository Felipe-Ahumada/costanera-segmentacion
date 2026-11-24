"""Carga y validación del archivo de clientes (paquete 2.2.1, RF.1 y RNF.3)."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import config


@dataclass
class ResumenCarga:
    registros_origen: int
    registros_cargados: int
    rechazados: pd.DataFrame = field(repr=False)
    faltantes: dict
    duplicados_id: int

    @property
    def cuadra(self) -> bool:
        """El conteo de origen es igual a cargados + rechazados (criterio de RF.1)."""
        return self.registros_origen == self.registros_cargados + len(self.rechazados)

    def texto(self) -> str:
        lineas = [
            f"Registros en el archivo de origen: {self.registros_origen}",
            f"Registros cargados:                {self.registros_cargados}",
            f"Registros rechazados:              {len(self.rechazados)}",
            f"Duplicados por identificador:      {self.duplicados_id}",
            f"Conteo cuadra (origen = cargados + rechazados): {'sí' if self.cuadra else 'NO'}",
        ]
        if len(self.rechazados):
            lineas.append("Motivos de rechazo:")
            for motivo, n in self.rechazados["motivo"].value_counts().items():
                lineas.append(f"  - {motivo}: {n}")
        return "\n".join(lineas)


def leer_archivo(ruta=config.DATOS_CRUDOS) -> pd.DataFrame:
    """Lee el archivo de Fidelización (Excel o CSV) y normaliza los nombres de columna."""
    ruta = str(ruta)
    df = pd.read_csv(ruta) if ruta.endswith(".csv") else pd.read_excel(ruta)
    df.columns = [c.strip() for c in df.columns]
    return df.rename(columns=config.COLUMNAS)


def _motivos_rechazo(df: pd.DataFrame) -> pd.Series:
    motivos = pd.Series("", index=df.index)

    def marcar(mascara, texto):
        motivos.loc[mascara & (motivos == "")] = texto

    for col in config.COLUMNAS_OBLIGATORIAS:
        if col in df:
            marcar(df[col].isna(), f"falta {col}")
        else:
            motivos[:] = f"columna {col} ausente"
    marcar(~df["genero"].isin(config.GENEROS_VALIDOS), "género fuera de catálogo")
    for col, (lo, hi) in config.RANGOS_VALIDOS.items():
        valores = pd.to_numeric(df[col], errors="coerce")
        marcar(~valores.between(lo, hi), f"{col} fuera de rango [{lo}, {hi}]")
    marcar(df["id_cliente"].duplicated(keep="first"), "identificador duplicado")
    return motivos


def cargar(ruta=config.DATOS_CRUDOS) -> tuple[pd.DataFrame, ResumenCarga]:
    """Devuelve los registros válidos y el resumen de carga con los rechazados y su motivo."""
    df = leer_archivo(ruta)
    motivos = _motivos_rechazo(df)
    rechazados = df[motivos != ""].assign(motivo=motivos[motivos != ""])
    validos = df[motivos == ""].copy()
    for col in ["edad", "ingreso_anual_k", "indice_gasto"]:
        validos[col] = pd.to_numeric(validos[col])
    resumen = ResumenCarga(
        registros_origen=len(df),
        registros_cargados=len(validos),
        rechazados=rechazados,
        faltantes=df.isna().sum().to_dict(),
        duplicados_id=int(df["id_cliente"].duplicated().sum()),
    )
    return validos.reset_index(drop=True), resumen
