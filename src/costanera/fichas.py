"""Fichas de perfil por segmento y exportación para Marketing (RF.3, RF.6 y RF.7)."""
import pandas as pd

from . import config

NIVELES = ["bajo", "medio", "alto"]

PERFILES = {
    ("alto", "alto"): ("Premium", "Ingreso y gasto altos. Fidelizar con beneficios exclusivos y "
                                  "preventas; cuidar la experiencia más que el precio."),
    ("alto", "bajo"): ("Potencial por activar", "Ingreso alto pero gasta poco en el centro. Invitar "
                                                "a conocer tiendas de mayor valor y servicios."),
    ("bajo", "alto"): ("Entusiastas", "Gastan mucho en relación con su ingreso. Campañas de "
                                      "fidelización con puntos; evitar empujar endeudamiento."),
    ("bajo", "bajo"): ("Sensibles al precio", "Ingreso y gasto bajos. Ofertas de valor, patio de "
                                              "comidas y eventos gratuitos."),
}
PERFIL_MEDIO = ("Estándar", "Ingreso y gasto cercanos al promedio. Campañas generales y "
                            "comunicación de novedades.")


def _nivel(valor, corte_bajo, corte_alto):
    return "bajo" if valor < corte_bajo else ("alto" if valor > corte_alto else "medio")


def construir_fichas(base: pd.DataFrame, col_segmento: str = "segmento") -> pd.DataFrame:
    """Una fila por segmento: tamaño, medias, composición y un nombre en lenguaje claro."""
    q = {v: base[v].quantile([1 / 3, 2 / 3]).values for v in config.VARIABLES_MODELO}
    filas = []
    for seg, g in base[base[col_segmento] > 0].groupby(col_segmento):
        ing, gas = g["ingreso_anual_k"].mean(), g["indice_gasto"].mean()
        clave = (_nivel(ing, *q["ingreso_anual_k"]), _nivel(gas, *q["indice_gasto"]))
        nombre, accion = PERFILES.get(clave, PERFIL_MEDIO)
        fila = {
            "segmento": int(seg),
            "nombre": nombre,
            "clientes": len(g),
            "pct_clientes": round(len(g) / len(base) * 100, 1),
            "edad_media": round(g["edad"].mean(), 1),
            "ingreso_medio_k": round(ing, 1),
            "indice_gasto_medio": round(gas, 1),
            "pct_mujeres": round((g["genero"] == "F").mean() * 100, 1),
        }
        for tramo in config.ETIQUETAS_TRAMOS:
            fila[f"pct_{tramo}"] = round((g["tramo_etario"] == tramo).mean() * 100, 1)
        fila["accion_sugerida"] = accion
        filas.append(fila)
    fichas = pd.DataFrame(filas)
    # Alerta de equidad: segmentos donde algún tramo etario queda casi sin representación
    tramos = [f"pct_{t}" for t in config.ETIQUETAS_TRAMOS]
    fichas["alerta_equidad"] = fichas[tramos].min(axis=1).apply(
        lambda m: "Revisar: un tramo etario casi no aparece; la campaña no puede excluir "
                  "beneficios base (RF.9)" if m < 5 else "")
    return fichas


def exportar(base: pd.DataFrame, fichas: pd.DataFrame, version: str) -> str:
    """Excel para Marketing: fichas + lista seudonimizada por segmento (sin nombre, RUT ni correo)."""
    prohibidas = {"id_cliente", "nombre", "rut", "correo", "email"}
    assert not prohibidas & set(base.columns), "La exportación no puede llevar identificadores directos"
    config.REPORTES.mkdir(parents=True, exist_ok=True)
    ruta = config.REPORTES / f"fichas_segmentos_{version}.xlsx"
    columnas = ["seudonimo", "segmento", "genero", "tramo_etario", "ingreso_anual_k", "indice_gasto"]
    with pd.ExcelWriter(ruta) as w:
        fichas.to_excel(w, sheet_name="Fichas de perfil", index=False)
        base[columnas].sort_values("segmento").to_excel(w, sheet_name="Clientes por segmento", index=False)
    return str(ruta)
