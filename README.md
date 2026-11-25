# Segmentación de clientes de Costanera Andina

Este proyecto agrupa a los clientes del programa de fidelización de un centro comercial según su ingreso anual y su índice de gasto, para que el equipo de Marketing pueda diseñar una campaña distinta para cada grupo en lugar de una sola campaña para todos. Lo desarrollamos para la asignatura Gestión de Proyectos de Datos (SCY1102) de Duoc UC, siguiendo la metodología CRISP-DM en iteraciones.

## Qué hace

La versión 1 de la herramienta lee el archivo de clientes, revisa que los datos estén completos y sin duplicados, reemplaza el identificador de cada cliente por un seudónimo y agrupa a los clientes con K-means, entre 3 y 8 segmentos. Al final muestra cuántos clientes tiene cada segmento y guarda la base con el segmento de cada cliente. Edad y género no entran al modelo, para que ninguna campaña discrimine por ellos.

Con los datos actuales se forman cinco segmentos. Los grupos quedan bien separados (silueta de 0,555) y se mantienen casi iguales cuando se cambia la muestra (estabilidad de 0,976). Las fichas de perfil, la revisión de equidad por edad y género y la exportación a Excel son de la versión 2, que está en desarrollo.

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

El número de segmentos se puede cambiar entre 3 y 8. Al terminar, el programa muestra un resumen de la carga, el control técnico y el tamaño de cada segmento, y guarda la base en data/processed.

Para correr las pruebas:

```bash
pytest -q
```

Si quieres revisar el análisis paso a paso, abre los notebooks con `jupyter notebook` y síguelos en orden: primero la comprensión de los datos, luego la preparación y después la iteración 1 del modelo.

## Cómo está organizado

La carpeta data/raw tiene el archivo de entrada. En src/costanera está el código de la herramienta, separado por etapa: carga, preparación, modelado y evaluación. La carpeta notebooks tiene un notebook por etapa con sus resultados, y en tests están las pruebas. Las carpetas data/processed y reports se crean solas al ejecutar el proyecto, por eso no se suben al repositorio.

## Versiones

Cada iteración terminada tiene su etiqueta. La etiqueta v1-iteracion1 corresponde al modelo base. La iteración 2 (comparación de algoritmos, fichas de perfil y revisión de equidad) está en curso y su etiqueta se creará cuando termine su evaluación con Marketing (H3, 04/12/2026). El trabajo adelantado de las iteraciones 2 y 3 está en la rama desarrollo-anticipado.

## Sobre los datos

El archivo Mall_Customers.xlsx es un conjunto público de práctica con 200 clientes. Costanera Andina es un caso académico, así que los datos no corresponden a personas reales.

## Autores

Felipe Ahumada Silva y Francisca Carrasco Lozano
