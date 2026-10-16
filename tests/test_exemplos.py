"""Trava o parecer esperado de CADA arquivo de exemplos/.

Se alguém mudar uma regra e um exemplo mudar de parecer, este teste grita na
hora — os exemplos do README nunca ficam mentindo.
"""
import json
from pathlib import Path

import pytest

from triagem.modelo import RECUSADA, REVISAO_HUMANA, SEGUE
from triagem.triagem import triar

PASTA = Path(__file__).resolve().parents[1] / "exemplos"

# (arquivo, parecer esperado, regras dos motivos)
CASOS = [
    # --- os 5 do enunciado (seção 4) ---
    ("P-001.json", SEGUE, []),
    ("P-002.json", RECUSADA, ["R1"]),
    ("P-003.json", REVISAO_HUMANA, ["R5"]),
    ("P-004.json", RECUSADA, ["R2", "R3"]),
    ("P-005.json", REVISAO_HUMANA, ["R4", "R6"]),
    # --- borda: R1 ---
    ("borda/area_100ha_exata.json", SEGUE, []),
    ("borda/area_99_9ha.json", RECUSADA, ["R1"]),
    # --- borda: R2 ---
    ("borda/alerta_no_dia_do_corte.json", SEGUE, []),
    ("borda/alerta_um_dia_depois.json", RECUSADA, ["R2"]),
    ("borda/alerta_lista_sem_recusa.json", SEGUE, []),
    ("borda/alerta_lista_com_recusa.json", RECUSADA, ["R2"]),
    ("borda/alerta_ilegivel.json", REVISAO_HUMANA, ["R2"]),
    ("borda/alerta_lista_com_ilegivel.json", REVISAO_HUMANA, ["R2"]),
    # --- borda: R3 ---
    ("borda/car_minusculo_espacado.json", SEGUE, []),
    ("borda/car_fora_da_lista.json", REVISAO_HUMANA, ["R3"]),
    # --- borda: R4 ---
    ("borda/cadastral_pendente.json", REVISAO_HUMANA, ["R4"]),
    # --- borda: R5 ---
    ("borda/divergencia_5pct_exata.json", SEGUE, []),
    ("borda/divergencia_5pct_acima.json", REVISAO_HUMANA, ["R5"]),
    # --- borda: R6 ---
    ("borda/area_negativa.json", REVISAO_HUMANA, ["R6"]),
    ("borda/area_como_texto.json", REVISAO_HUMANA, ["R6"]),
    ("borda/campo_id_ausente.json", REVISAO_HUMANA, ["R6"]),
    ("borda/todos_campos_ausentes.json", REVISAO_HUMANA, ["R6"] * 7),
]


@pytest.mark.parametrize("arquivo,parecer,motivos", CASOS)
def test_parecer_do_exemplo(arquivo, parecer, motivos):
    proposta = json.loads((PASTA / arquivo).read_text(encoding="utf-8"))
    resultado = triar(proposta)
    assert resultado.parecer == parecer
    assert [m.regra for m in resultado.motivos] == motivos
