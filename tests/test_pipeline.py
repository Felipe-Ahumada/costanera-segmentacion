"""Pruebas de los criterios de aceptación que se pueden automatizar."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from costanera import carga, config, fichas, pipeline, preparacion  # noqa: E402


@pytest.fixture(scope="module")
def corrida():
    return pipeline.ejecutar(k=5, version="test", registrar=False)


def test_rf1_conteo_de_carga_cuadra():
    _, resumen = carga.cargar()
    assert resumen.cuadra
    assert resumen.registros_origen == 200


def test_rf1_rechaza_registros_invalidos_con_motivo(tmp_path):
    df = carga.leer_archivo().rename(columns={v: k for k, v in config.COLUMNAS.items()})
    malo = pd.concat([df, df.iloc[[0]]], ignore_index=True)       # duplicado
    malo.loc[len(malo)] = [999, "X", 30, "Graduate", "Single", 50, 50]  # género inválido
    ruta = tmp_path / "prueba.csv"
    malo.to_csv(ruta, index=False)
    validos, resumen = carga.cargar(ruta)
    assert resumen.cuadra
    assert len(resumen.rechazados) == 2
    assert set(resumen.rechazados["motivo"]) == {"identificador duplicado", "género fuera de catálogo"}


def test_rnf3_base_sin_duplicados_y_completa(corrida):
    base = corrida["base"]
    assert base["seudonimo"].is_unique
    assert base[config.VARIABLES_MODELO].notna().mean().min() >= 0.95


def test_rnf4_sin_identificadores_directos(corrida):
    assert "id_cliente" not in corrida["base"]
    xls = pd.read_excel(corrida["ruta_excel"], sheet_name="Clientes por segmento")
    assert not {"id_cliente", "nombre", "rut", "correo"} & set(xls.columns)


def test_rf3_todos_los_segmentos_tienen_ficha(corrida):
    assert set(corrida["fichas"]["segmento"]) == set(corrida["base"]["segmento"])


def test_rf10_recalculo_da_los_mismos_resultados(corrida):
    otra = pipeline.ejecutar(k=5, version="test", registrar=False)
    assert (otra["base"]["segmento"].values == corrida["base"]["segmento"].values).all()


def test_seudonimo_estable():
    assert preparacion.seudonimo(1) == preparacion.seudonimo(1)
    assert preparacion.seudonimo(1) != preparacion.seudonimo(2)
