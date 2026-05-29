from src.controller.autoDensidad.calculoPorRetenidos.core.auditoria_decision import (
    TIPO_CURVA_PASANTE_ACUMULADO,
    TIPO_CURVA_RETENIDO_ACUMULADO,
    TIPO_CURVA_RETENIDO_INDIVIDUAL,
    generar_auditoria_completa,
)


def test_brita2_no_dispara_eliminacion_por_retenido_individual_valido():
    brita2 = {
        "nombre": "Brita 2",
        "retido_ind_pct": [1, 21, 72, 4, 1],
        "proporcion_pct": 0.0,
    }

    resultado = generar_auditoria_completa(
        pasante_real=[99, 78, 6, 2, 1],
        banda_min=[85, 60, 10, 2, 0],
        banda_max=[100, 90, 40, 15, 5],
        tamices=[6.3, 4.8, 2.4, 1.2, 0.6],
        materiales=[brita2],
        proporciones_optimizadas={"Brita 2": 0.0, "total_pct": 100.0},
    )

    problemas_criticos = resultado["auditoria_industrial"]["problemas_criticos"]
    titulos = {problema["titulo"] for problema in problemas_criticos}

    assert "Material único eliminado" not in titulos
    assert resultado["auditoria_industrial"]["validacion_materiales"]["materiales_unicos"] == []


def test_auditoria_expone_tipos_de_curva_en_trazabilidad():
    material = {
        "nombre": "Brita 2",
        "retido_ind_pct": [1, 21, 72, 4, 1],
        "proporcion_pct": 25.0,
    }

    resultado = generar_auditoria_completa(
        pasante_real=[99, 78, 6, 2, 1],
        banda_min=[85, 60, 10, 2, 0],
        banda_max=[100, 90, 40, 15, 5],
        tamices=[6.3, 4.8, 2.4, 1.2, 0.6],
        materiales=[material],
        proporciones_optimizadas={"Brita 2": 25.0, "total_pct": 100.0},
    )

    trazabilidad = resultado["trazabilidad_curvas"]
    trazabilidad_material = resultado["auditoria_industrial"]["validacion_materiales"]["trazabilidad"]

    assert trazabilidad["entrada_principal"] == TIPO_CURVA_PASANTE_ACUMULADO
    assert TIPO_CURVA_RETENIDO_INDIVIDUAL in trazabilidad["tipos_soportados_material"]
    assert TIPO_CURVA_RETENIDO_ACUMULADO in trazabilidad["tipos_soportados_material"]
    assert TIPO_CURVA_PASANTE_ACUMULADO in trazabilidad["tipos_soportados_material"]
    assert trazabilidad_material[0]["tipo_curva_origen"] == TIPO_CURVA_RETENIDO_INDIVIDUAL