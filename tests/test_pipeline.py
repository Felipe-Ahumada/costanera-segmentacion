"""Pruebas de los criterios de aceptación que se pueden automatizar."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from costanera import carga, config, fichas, monitoreo, pipeline, preparacion  # noqa: E402


@pytest.fixture(scope="module")
def corrida():
    return pipeline.ejecutar(k=5, version="test", registrar=False)


@pytest.fixture(scope="module")
def corrida_v2():
    return pipeline.ejecutar(k=5, version="test_v2", consentimiento=None, registrar=False)


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


def test_rnf4_version_final_solo_con_consentimiento(corrida):
    base = corrida["base"]
    assert base["consentimiento"].all()
    assert len(base) == corrida["resumen_consentimiento"]["con_consentimiento"]


def test_rf5_todo_cliente_con_consentimiento_tiene_segmento(corrida):
    assert (corrida["base"]["segmento"] > 0).all()


def test_rf11_compara_con_la_segmentacion_anterior(corrida_v2):
    r = pipeline.ejecutar(k=5, version="test", anterior=corrida_v2["ruta_base"], registrar=False)
    c = r["comparacion"]
    assert c["clientes_comparados"] == len(r["base"])
    assert c["matriz"].values.sum() == c["clientes_comparados"]


def test_rf12_avisa_cuando_los_datos_cambian(corrida):
    base = corrida["base"]
    assert not monitoreo.alerta_deriva(base, base)["alerta"].any()
    futura = base.assign(ingreso_anual_k=base["ingreso_anual_k"] * 1.3)
    assert monitoreo.alerta_deriva(base, futura).set_index("variable").loc["ingreso_anual_k", "alerta"]


def test_rnf12_registro_de_ejecuciones(tmp_path):
    ruta = tmp_path / "registro.csv"
    monitoreo.registrar_ejecucion("test", "archivo.xlsx", 5, 172, 0, ruta=ruta)
    monitoreo.registrar_ejecucion("test", "archivo.xlsx", 5, 172, 1, ruta=ruta)
    assert monitoreo.resumen_uso(ruta)["ejecuciones"] == 2
    assert "seudonimo" not in pd.read_csv(ruta).columns
