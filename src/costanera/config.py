"""Parámetros del proyecto SCA-2026-01 (segmentación de clientes de Costanera Andina).

Todo lo que decide el comportamiento del pipeline vive aquí, para que el recálculo
(RF.10) dé los mismos resultados con la misma base.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS_CRUDOS = RAIZ / "data" / "raw" / "Mall_Customers.xlsx"
DATOS_PROCESADOS = RAIZ / "data" / "processed"
REPORTES = RAIZ / "reports"
FIGURAS = REPORTES / "figuras"
REGISTRO_EXPERIMENTOS = REPORTES / "registro_experimentos.csv"

SEMILLA = 42

# Nombres de columnas del archivo de Fidelización -> nombres internos
COLUMNAS = {
    "CustomerID": "id_cliente",
    "Gender": "genero",
    "Age": "edad",
    "Education": "educacion",
    "Marital Status": "estado_civil",
    "Annual Income (k$)": "ingreso_anual_k",
    "Spending Score (1-100)": "indice_gasto",
}
COLUMNAS_OBLIGATORIAS = ["id_cliente", "genero", "edad", "ingreso_anual_k", "indice_gasto"]

# Variables con las que se segmenta. Edad y género NO entran al modelo: se usan solo
# para revisar la composición de cada segmento (RF.6, riesgo R7).
VARIABLES_MODELO = ["ingreso_anual_k", "indice_gasto"]
VARIABLES_PROTEGIDAS = ["genero", "tramo_etario"]

TRAMOS_EDAD = [17, 29, 44, 59, 120]
ETIQUETAS_TRAMOS = ["18-29", "30-44", "45-59", "60+"]

# Reglas de validación de la carga (RF.1, RNF.3)
RANGOS_VALIDOS = {
    "edad": (18, 100),
    "ingreso_anual_k": (0, 1000),
    "indice_gasto": (1, 100),
}
GENEROS_VALIDOS = {"F", "M"}

# Control técnico interno de la evaluación (no son requerimientos del cliente)
CRITERIOS = {
    "silueta_min": 0.40,         # Rousseeuw (1987)
    "tamano_min_pct": 5.0,       # ningún segmento bajo 5 %
    "estabilidad_min": 0.80,     # ARI medio entre remuestreos
    "brecha_max_pp": 15.0,       # brecha máxima de composición, en puntos porcentuales
}
REMUESTREOS = 30
