# Procedimiento de recálculo y monitoreo de la segmentación

Paquete 2.6.4 del proyecto SCA-2026-01. Este procedimiento lo sigue el Área de TI o el Analista de Datos cada vez que Fidelización entrega un archivo nuevo de clientes. Se probó el 15/01/2027: una persona distinta de quien construyó el modelo lo ejecutó en menos de una jornada y obtuvo los mismos segmentos (RF.10).

## Cuándo se recalcula

Una vez por trimestre, o antes si Marketing lanza una campaña grande o si la herramienta muestra un aviso de cambio en los datos.

## Pasos

1. Pedir a Fidelización dos archivos: el de clientes (mismo formato que Mall_Customers.xlsx) y el de consentimiento vigente (mismo formato que consentimiento_renovacion_2026-12.csv). Guardarlos en data/raw.
2. Activar el entorno del proyecto y ejecutar la herramienta indicando la base anterior:

```bash
export PYTHONPATH=src
python -m costanera.pipeline --archivo data/raw/<archivo nuevo> --consentimiento data/raw/<consentimiento nuevo> --segmentos 5 --version <AAAA-MM> --anterior data/processed/base_analitica_final.csv
```

3. Revisar el resumen que muestra la herramienta, en este orden:
   1. Resumen de carga: el conteo debe cuadrar y los rechazados deben tener motivo.
   2. Consentimiento: si quedan menos de 150 clientes, informar la limitación a Marketing antes de usar los segmentos.
   3. Control técnico: si la silueta baja de 0,40, algún segmento queda bajo 5 % o la estabilidad baja de 0,80, no se publica la nueva segmentación y se avisa al Jefe de Proyecto.
   4. Aviso de cambio en los datos (PSI sobre 0,20): los clientes cambiaron; revisar con Marketing si conviene probar otro número de segmentos.
   5. Comparación con la segmentación anterior: si más del 20 % de los clientes cambia de segmento, las fichas deben volver a validarse con Marketing.
   6. Brecha por edad y por género: se informa siempre junto con las fichas.
4. Entregar a Marketing el Excel de reports/fichas_segmentos_<versión>.xlsx. No enviar la base analítica ni ningún archivo con el identificador original.
5. Anotar el recálculo en el registro de ejecuciones (lo hace la herramienta sola) y en la bitácora del área.

## Retención

La base analítica de cada recálculo se conserva un año y después se elimina, según la política de retención aprobada en el proyecto (RNF.7). Los archivos de data/raw se borran del equipo una vez terminado el recálculo.
