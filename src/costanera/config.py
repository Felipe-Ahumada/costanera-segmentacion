"""Parámetros del proyecto SCA-2026-01 (segmentación de clientes de Costanera Andina).

Todo lo que decide el comportamiento del pipeline vive aquí, para que el recálculo
(RF.10) dé los mismos resultados con la misma base.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS_CRUDOS = RAIZ / "data" / "raw" / "Mall_Customers.xlsx"
# Respuesta a la campaña de renovación de consentimiento (Ley 21.719), cerrada el 22/12/2026
CONSENTIMIENTO = RAIZ / "data" / "raw" / "consentimiento_renovacion_2026-12.csv"
DATOS_PROCESADOS = RAIZ / "data" / "processed"
REPORTES = RAIZ / "reports"
FIGURAS = REPORTES / "figuras"
REGISTRO_EXPERIMENTOS = REPORTES / "registro_experimentos.csv"
REGISTRO_EJECUCIONES = REPORTES / "registro_ejecuciones.csv"

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

# Monitoreo de la herramienta final (RF.11 y RF.12)
PSI_ALERTA = 0.20          # índice de estabilidad poblacional sobre el que se avisa deriva
MIN_CONSENTIDOS = 150      # plan de contingencia de R14: bajo esto se informa la limitación
