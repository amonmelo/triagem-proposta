"""Orquestração: valida os campos (R6), aplica R1–R6 em ordem e decide.

Decisão do enunciado: se a proposta cai em RECUSADA e REVISÃO HUMANA ao
mesmo tempo, vale RECUSADA — mas TODOS os motivos vão para o parecer.
"""
from __future__ import annotations

from typing import Any, List, Optional

from .modelo import (
    RECUSADA,
    REVISAO_HUMANA,
    SEGUE,
    EntradaInvalida,
    Parecer,
    ResultadoRegra,
    Violacao,
    pior_parecer,
)
from .regras import (
    r1_area_degradada,
    r2_alerta_desmatamento,
    r3_situacao_car,
    r4_situacao_cadastral,
    r5_area_matricula_vs_car,
    validar_campos,
)


def _ok(regra: str, detalhe: str) -> ResultadoRegra:
    return ResultadoRegra(regra=regra, resultado="ok", detalhe=detalhe)


def _violacao(violacao: Violacao) -> ResultadoRegra:
    return ResultadoRegra(
        regra=violacao.regra,
        resultado="violacao",
        detalhe=violacao.mensagem,
        violacao=violacao,
    )


def _nao_avaliada(regra: str, motivo: str) -> ResultadoRegra:
    return ResultadoRegra(
        regra=regra,
        resultado="nao_avaliada",
        detalhe=f"Não avaliada: {motivo}",
    )


def triar(proposta: Any) -> Parecer:
    """Aplica as regras a uma proposta (dicionário) e devolve o Parecer."""
    if not isinstance(proposta, dict):
        raise EntradaInvalida(
            "A proposta precisa ser um objeto JSON com os 7 campos do formato sugerido."
        )

    validacao = validar_campos(proposta)
    valores = validacao["valores"]

    resultados: List[Optional[ResultadoRegra]] = []

    # R1 — área degradada
    if "area_degradada_ha" in valores:
        violacao, detalhe = r1_area_degradada(valores["area_degradada_ha"])
        resultados.append(_violacao(violacao) if violacao else _ok("R1", detalhe))
    else:
        resultados.append(
            _nao_avaliada("R1", "o campo `area_degradada_ha` tem problema registrado em R6.")
        )

    # R2 — alerta de desmatamento
    if "alerta_desmatamento" in valores:
        violacao, detalhe = r2_alerta_desmatamento(valores["alerta_desmatamento"])
        resultados.append(_violacao(violacao) if violacao else _ok("R2", detalhe))
    else:
        resultados.append(
            _nao_avaliada("R2", "o campo `alerta_desmatamento` tem problema registrado em R6.")
        )

    # R3 — situação do CAR
    if "situacao_car" in valores:
        violacao, detalhe = r3_situacao_car(valores["situacao_car"])
        resultados.append(_violacao(violacao) if violacao else _ok("R3", detalhe))
    else:
        resultados.append(
            _nao_avaliada("R3", "o campo `situacao_car` tem problema registrado em R6.")
        )

    # R4 — situação cadastral
    if "situacao_cadastral" in valores:
        violacao, detalhe = r4_situacao_cadastral(valores["situacao_cadastral"])
        resultados.append(_violacao(violacao) if violacao else _ok("R4", detalhe))
    else:
        resultados.append(
            _nao_avaliada("R4", "o campo `situacao_cadastral` tem problema registrado em R6.")
        )

    # R5 — matrícula x CAR
    campos_r5 = ("area_matricula_ha", "area_car_ha")
    faltando_r5 = [c for c in campos_r5 if c not in valores]
    if not faltando_r5:
        violacao, detalhe = r5_area_matricula_vs_car(
            valores["area_matricula_ha"], valores["area_car_ha"]
        )
        resultados.append(_violacao(violacao) if violacao else _ok("R5", detalhe))
    else:
        resultados.append(
            _nao_avaliada(
                "R5",
                f"{', '.join('`' + c + '`' for c in faltando_r5)} tem problema "
                "registrado em R6.",
            )
        )

    # R6 — validação dos campos (já calculada acima)
    resultados.extend(_violacao(v) for v in validacao["violacoes"])
    if not validacao["violacoes"]:
        resultados.append(
            _ok("R6", "Os 7 campos obrigatórios presentes e utilizáveis.")
        )

    avaliacoes = [r for r in resultados if r is not None]
    violacoes = [r.violacao for r in avaliacoes if r.violacao is not None]

    if violacoes:
        parecer_final = pior_parecer(*(v.parecer_sugerido for v in violacoes))
    else:
        parecer_final = SEGUE

    pendencias = []
    if parecer_final == REVISAO_HUMANA:
        pendencias = [
            {"regra": v.regra, "acao": v.pendencia}
            for v in violacoes
            if v.pendencia
        ]

    return Parecer(
        proposta_id=valores.get("id", "sem-id"),
        parecer=parecer_final,
        motivos=violacoes,
        pendencias=pendencias,
        regras=avaliacoes,
    )
