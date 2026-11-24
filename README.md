# Segmentación de clientes de Costanera Andina

Este proyecto agrupa a los clientes del programa de fidelización de un centro comercial según su ingreso anual y su índice de gasto, para que el equipo de Marketing pueda diseñar una campaña distinta para cada grupo en lugar de una sola campaña para todos. Lo desarrollamos para la asignatura Gestión de Proyectos de Datos (SCY1102) de Duoc UC, siguiendo la metodología CRISP-DM en iteraciones.

## Qué hace

La herramienta lee el archivo de clientes, revisa que los datos estén completos y sin duplicados, deja solo a los clientes que renovaron su consentimiento (Ley 21.719), reemplaza el identificador de cada cliente por un seudónimo y agrupa a los clientes con K-means. Al final entrega un Excel con una ficha por segmento y la lista de clientes de cada uno. También revisa que los segmentos no dejen fuera a algún grupo de edad o de género, porque la idea es que ninguna campaña discrimine.

Cuando se recalcula, compara la segmentación nueva con la anterior para decir cuántos clientes cambiaron de segmento, avisa si los datos de entrada cambiaron mucho y deja un registro de cada ejecución.

Con los datos actuales se forman cinco segmentos: Premium, Entusiastas, Estándar, Sensibles al precio y Potencial por activar. En la versión final, con los 172 clientes que renovaron su consentimiento, los grupos quedan bien separados (silueta de 0,538) y se mantienen casi iguales cuando se cambia la muestra (estabilidad de 0,958). Solo un cliente cambió de segmento respecto de la versión anterior. Antes de quedarnos con K-means lo comparamos con un agrupamiento jerárquico, que llegó a los mismos segmentos, y con DBSCAN, que dejaba clientes sin grupo.

## Requisitos

Python 3.9 o superior. Las librerías necesarias están en requirements.txt.

## Instalación

```bash
git clone https://github.com/Felipe-Ahumada/costanera-segmentacion.git
cd costanera-segmentacion
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Cómo usarlo

Para segmentar desde la terminal:

```bash
export PYTHONPATH=src            # en Windows: set PYTHONPATH=src
python -m costanera.pipeline --segmentos 5
```

El número de segmentos se puede cambiar entre 3 y 8. Por defecto se usan solo los clientes con consentimiento vigente, según el archivo data/raw/consentimiento_renovacion_2026-12.csv. Al terminar, el programa muestra un resumen de la carga, del consentimiento y del control de calidad, y guarda los resultados en la carpeta reports.

Para recalcular y comparar con una segmentación anterior se agrega la base anterior:

```bash
python -m costanera.pipeline --segmentos 5 --anterior data/processed/base_analitica_v2.csv
```

Los pasos completos para recalcular están en docs/procedimiento_recalculo.md, y la guía para Marketing en docs/manual_marketing.md.

Para correr las pruebas:

```bash
pytest -q
```

Si quieres revisar el análisis paso a paso, abre los notebooks con `jupyter notebook` y síguelos en orden: primero la comprensión de los datos, luego la preparación y después las tres iteraciones del modelo.

## Cómo está organizado

La carpeta data/raw tiene los archivos de entrada: el de clientes y el de consentimiento. En src/costanera está el código de la herramienta, separado por etapa: carga, preparación, modelado, evaluación, fichas y monitoreo. La carpeta notebooks tiene un notebook por etapa con sus resultados, en docs están el procedimiento de recálculo y el manual para Marketing, y en tests están las pruebas. Las carpetas data/processed y reports se crean solas al ejecutar el proyecto, por eso no se suben al repositorio.

## Versiones

Cada iteración terminada tiene su etiqueta. La etiqueta v1-iteracion1 corresponde al modelo base, v2-iteracion2 a la comparación de algoritmos, las fichas de perfil y la revisión de equidad, y v3-final a la versión entregada a Marketing, construida solo con clientes con consentimiento y con la comparación entre versiones y el aviso de cambios en los datos.

## Sobre los datos

El archivo Mall_Customers.xlsx es un conjunto público de práctica con 200 clientes. Costanera Andina es un caso académico, así que los datos no corresponden a personas reales. Como ese archivo no trae consentimiento, la respuesta a la campaña de renovación está simulada con una semilla fija.

## Autores

Felipe Ahumada Silva y Francisca Carrasco Lozano
