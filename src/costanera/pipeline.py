"""Herramienta de segmentación de punta a punta (versión 1: paquete 2.6.1, RF.1, RF.2, RF.10).

Uso (Marketing no escribe código, solo ejecuta el comando):

    python -m costanera.pipeline --archivo data/raw/Mall_Customers.xlsx --segmentos 5

Muestra el resumen de carga, el control técnico y el tamaño de cada segmento, y deja la base
analítica seudonimizada con el segmento de cada cliente en data/processed. Las fichas de perfil,
la composición por edad y género y la exportación para Marketing son de la versión 2 (2.6.2).
"""
import argparse
import sys

from . import carga, config, evaluacion, modelado, preparacion


def ejecutar(archivo=config.DATOS_CRUDOS, k: int = 5, version: str = "v1",
             solo_con_consentimiento: bool = False, registrar: bool = True) -> dict:
    validos, resumen = carga.cargar(archivo)
    base = preparacion.preparar(validos, solo_con_consentimiento)
    X, _ = preparacion.escalar(base)
    km = modelado.kmeans(X, k)
    base["segmento"] = modelado.ordenar_etiquetas(km.labels_, base["indice_gasto"].values)
    resultado = evaluacion.evaluar(X, base["segmento"].values, base, k)
    chequeos = evaluacion.veredicto(resultado)
    tamanos = base.groupby("segmento").agg(clientes=("segmento", "size"),
                                           ingreso_medio_k=("ingreso_anual_k", "mean"),
                                           indice_gasto_medio=("indice_gasto", "mean")).round(1)
    tamanos["pct_clientes"] = (tamanos["clientes"] / len(base) * 100).round(1)
    ruta_base = preparacion.guardar_base(base, version)
    if registrar:
        evaluacion.registrar_experimento(version, "K-means", f"k={k}", config.VARIABLES_MODELO,
                                         resultado, "ejecución del pipeline")
    return {"resumen_carga": resumen, "resultado": resultado, "chequeos": chequeos,
            "segmentos": tamanos.reset_index(), "base": base, "ruta_base": ruta_base}


def main(argv=None):
    p = argparse.ArgumentParser(description="Segmentación de clientes de Costanera Andina")
    p.add_argument("--archivo", default=str(config.DATOS_CRUDOS))
    p.add_argument("--segmentos", type=int, default=5, choices=range(3, 9),
                   help="cantidad de segmentos, entre 3 y 8 (RF.2)")
    p.add_argument("--version", default="v1")
    p.add_argument("--solo-con-consentimiento", action="store_true")
    a = p.parse_args(argv)
    r = ejecutar(a.archivo, a.segmentos, a.version, a.solo_con_consentimiento)
    print("== Resumen de carga ==")
    print(r["resumen_carga"].texto())
    print("\n== Control técnico ==")
    for nombre, ok in r["chequeos"].items():
        print(f"  [{'OK' if ok else 'REVISAR'}] {nombre}")
    print("\n== Segmentos ==")
    print(r["segmentos"][["segmento", "clientes", "pct_clientes", "ingreso_medio_k",
                          "indice_gasto_medio"]].to_string(index=False))
    print(f"\nBase analítica seudonimizada: {r['ruta_base']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
