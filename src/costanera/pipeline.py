"""Herramienta de segmentación de punta a punta (paquetes 2.6.1 a 2.6.3).

Uso (Marketing no escribe código, solo ejecuta el comando):

    python -m costanera.pipeline --segmentos 5

Por defecto trabaja solo con los clientes que renovaron su consentimiento (RNF.4) y, si se le
indica una segmentación anterior, la compara con la nueva (RF.11) y avisa si los datos cambiaron
mucho (RF.12). Genera, en reports/: las fichas de perfil con la lista de clientes por segmento
(Excel), la base analítica versionada y una línea en el registro de ejecuciones (RNF.12).
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

from . import carga, config, evaluacion, fichas, modelado, monitoreo, preparacion


def ejecutar(archivo=config.DATOS_CRUDOS, k: int = 5, version: str = "final",
             consentimiento=config.CONSENTIMIENTO, anterior=None,
             registrar: bool = True) -> dict:
    """Corre la herramienta completa.

    consentimiento: archivo de la campaña de renovación; None para trabajar con toda la base
                    (solo sirve para reproducir las iteraciones 1 y 2, anteriores a la ley).
    anterior: base analítica de una ejecución previa, para comparar (RF.11) y medir deriva (RF.12).
    """
    validos, resumen = carga.cargar(archivo)
    resumen_consentimiento = None
    if consentimiento is not None:
        validos, resumen_consentimiento = carga.agregar_consentimiento(validos, consentimiento)
    base = preparacion.preparar(validos, solo_con_consentimiento=consentimiento is not None)
    X, _ = preparacion.escalar(base)
    km = modelado.kmeans(X, k)
    base["segmento"] = modelado.ordenar_etiquetas(km.labels_, base["indice_gasto"].values)
    resultado = evaluacion.evaluar(X, base["segmento"].values, base, k)
    chequeos = evaluacion.veredicto(resultado)
    tabla = fichas.construir_fichas(base)
    base["nombre_segmento"] = base["segmento"].map(tabla.set_index("segmento")["nombre"])

    deriva = comparacion = None
    if anterior is not None and Path(anterior).exists():
        previa = pd.read_csv(anterior)
        deriva = monitoreo.alerta_deriva(previa, base)
        if "nombre_segmento" in previa:
            comparacion = monitoreo.comparar_segmentaciones(previa, base)

    ruta_base = preparacion.guardar_base(base, version)
    ruta_excel = fichas.exportar(base, tabla, version)
    if registrar:
        evaluacion.registrar_experimento(version, "K-means", f"k={k}", config.VARIABLES_MODELO,
                                         resultado, "ejecución del pipeline")
        monitoreo.registrar_ejecucion(version, Path(archivo).name, k, len(base),
                                      int(deriva["alerta"].sum()) if deriva is not None else 0)
    return {"resumen_carga": resumen, "resumen_consentimiento": resumen_consentimiento,
            "resultado": resultado, "chequeos": chequeos, "fichas": tabla, "base": base,
            "deriva": deriva, "comparacion": comparacion,
            "ruta_base": ruta_base, "ruta_excel": ruta_excel}


def main(argv=None):
    p = argparse.ArgumentParser(description="Segmentación de clientes de Costanera Andina")
    p.add_argument("--archivo", default=str(config.DATOS_CRUDOS))
    p.add_argument("--segmentos", type=int, default=5, choices=range(3, 9),
                   help="cantidad de segmentos, entre 3 y 8 (RF.2)")
    p.add_argument("--version", default="final")
    p.add_argument("--consentimiento", default=str(config.CONSENTIMIENTO),
                   help="archivo de la campaña de renovación de consentimiento")
    p.add_argument("--toda-la-base", action="store_true",
                   help="ignora el consentimiento (solo para reproducir las iteraciones 1 y 2)")
    p.add_argument("--anterior", default=None,
                   help="base analítica de una ejecución anterior, para comparar y medir deriva")
    a = p.parse_args(argv)
    r = ejecutar(a.archivo, a.segmentos, a.version,
                 None if a.toda_la_base else a.consentimiento, a.anterior)
    print("== Resumen de carga ==")
    print(r["resumen_carga"].texto())
    if r["resumen_consentimiento"]:
        c = r["resumen_consentimiento"]
        print(f"Con consentimiento vigente: {c['con_consentimiento']} de {c['clientes']} "
              f"({c['pct_con_consentimiento']} %)")
        if not c["sobre_minimo"]:
            print(f"  AVISO: menos de {config.MIN_CONSENTIDOS} clientes; informe la limitación a Marketing.")
    print("\n== Control técnico ==")
    for nombre, ok in r["chequeos"].items():
        print(f"  [{'OK' if ok else 'REVISAR'}] {nombre}")
    if r["deriva"] is not None:
        print("\n== Cambio en los datos respecto de la base anterior (RF.12) ==")
        for _, f in r["deriva"].iterrows():
            print(f"  {f['variable']}: PSI {f['psi']:.3f}" + ("  <- AVISO: los datos cambiaron" if f["alerta"] else ""))
    if r["comparacion"] is not None:
        c = r["comparacion"]
        print(f"\n== Comparación con la segmentación anterior (RF.11) ==\n  "
              f"{c['cambiaron']} de {c['clientes_comparados']} clientes cambiaron de segmento ({c['pct_cambiaron']} %)")
    print("\n== Segmentos ==")
    print(r["fichas"][["segmento", "nombre", "clientes", "pct_clientes", "ingreso_medio_k",
                        "indice_gasto_medio"]].to_string(index=False))
    print(f"\nFichas y listas para Marketing: {r['ruta_excel']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
