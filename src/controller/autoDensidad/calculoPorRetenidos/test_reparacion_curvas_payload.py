from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import _reparar_curvas_material_auditoria


def test_repara_100_fantasma_y_shift_en_payload_de_auditoria():
    tamices = [9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075]
    material_corrupto = {
        "nombre": "brita 2",
        "retido_ind_pct": [100, 0, 1, 21, 72, 4, 1, 0, 0],
        "pasantes": [0, 0, 1, 22, 94, 98, 99, 99, 99],
        "proporcion_pct": 33,
    }

    reparado = _reparar_curvas_material_auditoria(material_corrupto, tamices)

    assert reparado["tipo_curva_detectado"] == "pasantes_corruptos_shift_retido_acumulado"
    assert reparado["retido_ind_pct"] == [0.0, 1.0, 21.0, 72.0, 4.0, 1.0, 0.0, 0.0, 1.0]
    assert reparado["pasantes"] == [100.0, 99.0, 78.0, 6.0, 2.0, 1.0, 1.0, 1.0, 0.0]