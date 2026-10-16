"""Robustez: centenas de propostas aleatórias (e malformadas de propósito)
nunca quebram a triagem, sempre produzem um parecer válido e são
determinísticas. Semente fixa = o teste é reprodutível, não flaky."""
import random

from triagem.card import gerar_card
from triagem.modelo import (
    CAMPOS_OBRIGATORIOS,
    RECUSADA,
    REVISAO_HUMANA,
    SEGUE,
)
from triagem.triagem import triar

BONS = {
    "id": ["T-1", "T-2", "P-123"],
    "area_degradada_ha": [50, 100, 150.5, 900],
    "area_matricula_ha": [200, 1000, 2000],
    "area_car_ha": [180, 1000, 1900, 2100],
    "alerta_desmatamento": [
        None,
        "2020-01-01",
        "15/03/2023",
        ["2019-01-01", "01/01/2020"],
        "banana",
    ],
    "situacao_car": ["Ativo", "Pendente", "Cancelado", "Suspenso", "em análise"],
    "situacao_cadastral": ["Regular", "Pendente de regularização", "Baixada"],
}

MAUS = [
    None, "", "   ", -10, 0, True, False, "850", [], ["2020-01-02"], {},
    3.14, "32/13/2021", {"data": "2021-01-01"}, [None],
]

REGRAS = {"R1", "R2", "R3", "R4", "R5", "R6"}


def test_300_propostas_aleatorias_nunca_quebram_a_triagem():
    rng = random.Random(42)
    for _ in range(300):
        proposta = {}
        for campo in CAMPOS_OBRIGATORIOS:
            sorte = rng.random()
            if sorte < 0.12:
                continue  # campo ausente
            if sorte < 0.45:
                proposta[campo] = rng.choice(MAUS)
            else:
                proposta[campo] = rng.choice(BONS[campo])

        parecer = triar(proposta)  # não pode levantar exceção, nunca

        assert parecer.parecer in (SEGUE, RECUSADA, REVISAO_HUMANA)
        assert all(r.regra in REGRAS for r in parecer.regras)
        assert all(m.mensagem for m in parecer.motivos)

        if parecer.parecer == SEGUE:
            assert not parecer.motivos
        else:
            assert parecer.motivos

        # pendências só existem quando o parecer é revisão humana
        assert bool(parecer.pendencias) == (parecer.parecer == REVISAO_HUMANA)

        # o card sempre renderiza, com o id nele
        card = gerar_card(parecer)
        assert parecer.proposta_id in card

        # determinismo: mesma entrada, mesma saída, sempre
        assert parecer.to_dict() == triar(proposta).to_dict()
