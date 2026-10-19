"""Regras R1–R6 do teste e validação dos 7 campos obrigatórios.

Toda decisão aqui é determinística: mesma entrada, mesma saída, sem passar
pelo modelo. Cada função devolve (violacao_ou_None, detalhe_do_resultado).
"""
from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, Optional, Tuple

from .modelo import (
    AREA_MINIMA_DEGRADADA_HA,
    CORTE_DESMATAMENTO,
    RECUSADA,
    REVISAO_HUMANA,
    TOLERANCIA_AREA_PERCENTUAL,
    CAMPOS_OBRIGATORIOS,
    Violacao,
    citar,
    fmt_num,
    normalizar_texto,
)

_FORMATOS_DATA = ("%Y-%m-%d", "%d/%m/%Y")

# Texto usado na mensagem de R6, por campo, para dizer o que se esperava.
_ESPERADO = {
    "id": "texto não vazio",
    "area_degradada_ha": "número maior que zero",
    "area_matricula_ha": "número maior que zero",
    "area_car_ha": "número maior que zero",
    "alerta_desmatamento": "nulo, data (AAAA-MM-DD ou DD/MM/AAAA) ou lista de datas",
    "situacao_car": "texto: Ativo, Pendente, Cancelado ou Suspenso",
    "situacao_cadastral": "texto (ex.: Regular)",
}

_CAMPOS_DE_AREA = ("area_degradada_ha", "area_matricula_ha", "area_car_ha")


def _fmt_data(data: date) -> str:
    return data.strftime("%d/%m/%Y")


def interpretar_data(valor: Any) -> Optional[date]:
    """Aceita date/datetime, "AAAA-MM-DD" (com hora opcional) e "DD/MM/AAAA".

    Devolve None quando não reconhece. A hora é descartada: o corte da R2 é
    por dia — um alerta em 01/01/2020 às 23h59 ainda é do dia do corte.
    """
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if not isinstance(valor, str):
        return None
    texto = valor.strip()
    if "T" in texto:
        texto = texto.split("T", 1)[0]
    elif " " in texto:
        texto = texto.split(" ", 1)[0]
    if not texto:
        return None
    for formato in _FORMATOS_DATA:
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def _numero_valido(valor: Any) -> bool:
    # bool é subclasse de int em Python — true/false não é área. E o json do
    # Python aceita Infinity/NaN, que também não são área.
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
        and valor > 0
    )


def _r6_ausente(campo: str) -> Violacao:
    return Violacao(
        regra="R6",
        mensagem=f"Campo obrigatório ausente: `{campo}`.",
        parecer_sugerido=REVISAO_HUMANA,
        pendencia=f"Incluir o campo `{campo}` na proposta.",
    )


def _r6_inutilizavel(campo: str, valor: Any) -> Violacao:
    return Violacao(
        regra="R6",
        mensagem=(
            f"Campo obrigatório inutilizável: `{campo}` "
            f"(recebido: {citar(valor)}; esperado: {_ESPERADO[campo]})."
        ),
        parecer_sugerido=REVISAO_HUMANA,
        pendencia=(
            f"Corrigir o campo `{campo}` na proposta "
            f"(recebido: {citar(valor)}; esperado: {_ESPERADO[campo]})."
        ),
    )


def validar_campos(proposta: dict) -> dict:
    """R6 — confere os 7 campos obrigatórios do formato sugerido.

    Devolve {"violacoes": [...], "valores": {campo: valor_usável}}. Campo com
    problema não entra em `valores`, e as regras que dependem dele ficam
    "nao_avaliada" — o problema já está apontado na R6, sem motivo duplicado.

    Detalhe do enunciado: `alerta_desmatamento` NULO é dado válido
    (significa "sem alerta"); é a CHAVE AUSENTE que cai na R6. Para os
    outros campos, nulo e ausente são a mesma coisa.
    """
    violacoes: list = []
    valores: dict = {}
    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in proposta:
            violacoes.append(_r6_ausente(campo))
            continue
        valor = proposta[campo]

        if campo == "alerta_desmatamento":
            if valor is None:
                valores[campo] = None
            elif isinstance(valor, (str, date, datetime, list, tuple)):
                valores[campo] = valor
            else:
                violacoes.append(_r6_inutilizavel(campo, valor))
            continue

        if valor is None:
            violacoes.append(_r6_ausente(campo))
            continue

        if campo == "id":
            if isinstance(valor, str) and valor.strip():
                valores[campo] = valor.strip()
            else:
                violacoes.append(_r6_inutilizavel(campo, valor))
        elif campo in _CAMPOS_DE_AREA:
            if _numero_valido(valor):
                valores[campo] = float(valor)
            else:
                violacoes.append(_r6_inutilizavel(campo, valor))
        else:  # situacao_car, situacao_cadastral
            if isinstance(valor, str) and valor.strip():
                valores[campo] = valor
            else:
                violacoes.append(_r6_inutilizavel(campo, valor))
    return {"violacoes": violacoes, "valores": valores}


def r1_area_degradada(area_ha: float) -> Tuple[Optional[Violacao], str]:
    """R1 — área degradada de pelo menos 100 ha (exatamente 100 passa)."""
    if area_ha < AREA_MINIMA_DEGRADADA_HA:
        return (
            Violacao(
                regra="R1",
                mensagem=(
                    f"Área de pastagem degradada de {fmt_num(area_ha)} ha — "
                    f"abaixo do mínimo de {fmt_num(AREA_MINIMA_DEGRADADA_HA)} ha."
                ),
                parecer_sugerido=RECUSADA,
            ),
            f"Área degradada de {fmt_num(area_ha)} ha (abaixo do mínimo).",
        )
    return None, f"Área degradada de {fmt_num(area_ha)} ha (mínimo de 100 ha atendido)."


def _alerta_duvidoso(valor: Any, futuro: bool) -> Violacao:
    """Alerta que não dá para conferir contra o corte: vai para revisão."""
    if futuro:
        problema = "com data no futuro — provável erro de digitação"
        esperado = "a data informada ainda não chegou"
    else:
        problema = "em formato não reconhecido"
        esperado = "esperado: AAAA-MM-DD ou DD/MM/AAAA"
    return Violacao(
        regra="R2",
        mensagem=(
            f"Alerta de desmatamento {problema} "
            f"(recebido: {citar(valor)}); não dá para conferir o corte."
        ),
        parecer_sugerido=REVISAO_HUMANA,
        pendencia=(
            "Conferir a data do alerta de desmatamento com o proponente "
            f"({esperado})."
        ),
    )


def _recusa_r2(data: date) -> Violacao:
    return Violacao(
        regra="R2",
        mensagem=(
            f"Alerta de desmatamento em {_fmt_data(data)} — "
            f"posterior ao corte de {_fmt_data(CORTE_DESMATAMENTO)}."
        ),
        parecer_sugerido=RECUSADA,
    )


def r2_alerta_desmatamento(
    alerta: Any, hoje: Optional[date] = None
) -> Tuple[Optional[Violacao], str]:
    """R2 — nenhum alerta de desmatamento ESTRITAMENTE depois de 01/01/2020.

    Aceita nulo (sem alerta), uma data ou uma lista; basta um alerta depois
    do corte para recusar. Lista vazia equivale a sem alerta. Data ilegível
    ou no futuro (depois de `hoje`) não pode ser verificada, então vai para
    REVISÃO HUMANA citando o valor — erro de digitação não recusa ninguém.
    """
    hoje = hoje or date.today()
    if alerta is None:
        return None, "Sem alerta de desmatamento."

    if isinstance(alerta, (list, tuple)):
        if not alerta:
            return None, "Lista de alertas vazia (equivale a sem alerta)."
        datas: list = []
        duvidosos: list = []  # (valor, é_futuro)
        for item in alerta:
            data = interpretar_data(item)
            if data is None:
                duvidosos.append((item, False))
            elif data > hoje:
                duvidosos.append((item, True))
            else:
                datas.append(data)
        posteriores = [d for d in datas if d > CORTE_DESMATAMENTO]
        if posteriores:
            pior = max(posteriores)
            return (
                _recusa_r2(pior),
                f"Alertas verificados; o mais recente ({_fmt_data(pior)}) é posterior ao corte.",
            )
        if duvidosos:
            return (
                _alerta_duvidoso(*duvidosos[0]),
                "Alertas que não dá para conferir na lista.",
            )
        mais_recente = max(datas)
        return (
            None,
            f"Alertas todos até o corte (mais recente: {_fmt_data(mais_recente)}).",
        )

    data = interpretar_data(alerta)
    if data is None:
        return _alerta_duvidoso(alerta, False), "Alerta em formato não reconhecido."
    if data > hoje:
        return _alerta_duvidoso(alerta, True), "Alerta com data no futuro."
    if data > CORTE_DESMATAMENTO:
        return _recusa_r2(data), f"Alerta em {_fmt_data(data)}, depois do corte."
    return (
        None,
        f"Alerta em {_fmt_data(data)} — no dia do corte ou antes; não recusa.",
    )


_SITUACOES_CAR = ("ativo", "pendente", "cancelado", "suspenso")


def r3_situacao_car(valor: str) -> Tuple[Optional[Violacao], str]:
    """R3 — situação do CAR, com maiúsculas e espaços normalizados.

    Fora da lista conhecida vai para REVISÃO HUMANA citando o valor recebido.
    """
    normalizado = normalizar_texto(valor)
    if normalizado == "ativo":
        return None, "Situação do CAR \"Ativo\"."
    if normalizado == "pendente":
        return (
            Violacao(
                regra="R3",
                mensagem=(
                    f"Situação do CAR \"{normalizar_texto(valor).capitalize()}\" — "
                    "inscrição pendente exige verificação humana."
                ),
                parecer_sugerido=REVISAO_HUMANA,
                pendencia=(
                    "Obter a consulta atualizada da inscrição no CAR (SICAR) "
                    "e reapresentar a proposta."
                ),
            ),
            "Situação do CAR pendente.",
        )
    if normalizado in ("cancelado", "suspenso"):
        return (
            Violacao(
                regra="R3",
                mensagem=(
                    f"Situação do CAR \"{valor}\" — inscrição {normalizado} "
                    "impede a proposta."
                ),
                parecer_sugerido=RECUSADA,
            ),
            f"Situação do CAR \"{valor}\" (recusa direta).",
        )
    return (
        Violacao(
            regra="R3",
            mensagem=(
                f"Situação do CAR fora da lista conhecida "
                f"(recebido: \"{valor}\"; esperado: Ativo, Pendente, Cancelado ou Suspenso)."
            ),
            parecer_sugerido=REVISAO_HUMANA,
            pendencia=(
                "Confirmar a situação real da inscrição no CAR (SICAR) — "
                f"o valor recebido (\"{valor}\") não é reconhecido."
            ),
        ),
        "Situação do CAR fora da lista conhecida.",
    )


def r4_situacao_cadastral(valor: str) -> Tuple[Optional[Violacao], str]:
    """R4 — pelo enunciado, só "Regular" passa; qualquer outra vai para revisão.

    (A discussão de como isso fica com status reais de CNPJ está no DESIGN.md.)
    """
    if normalizar_texto(valor) == "regular":
        return None, "Situação cadastral \"Regular\"."
    return (
        Violacao(
            regra="R4",
            mensagem=(
                f"Situação cadastral \"{valor}\" — pelo enunciado, "
                "só \"Regular\" segue sem revisão humana."
            ),
            parecer_sugerido=REVISAO_HUMANA,
            pendencia=(
                "Obter comprovante atualizado da situação cadastral "
                f"(Receita Federal; recebido: \"{valor}\") e reapresentar a proposta."
            ),
        ),
        f"Situação cadastral \"{valor}\" (exige revisão).",
    )


def r5_area_matricula_vs_car(
    area_matricula: float, area_car: float
) -> Tuple[Optional[Violacao], str]:
    """R5 — diferença entre matrícula e CAR maior que 5% da matrícula revisa.

    "Maior que 5%" é estrito: exatamente 5% passa. Comparei multiplicando os
    dois lados por 100 em vez de dividir — mata o ruído de ponto flutuante
    no limite exato e não corre o risco de divisão por zero.
    """
    diferenca = abs(area_matricula - area_car)
    percentual = diferenca / area_matricula * 100 if area_matricula else 0.0
    if diferenca * 100 > TOLERANCIA_AREA_PERCENTUAL * area_matricula:
        return (
            Violacao(
                regra="R5",
                mensagem=(
                    f"Área da matrícula ({fmt_num(area_matricula)} ha) e área do CAR "
                    f"({fmt_num(area_car)} ha) divergem em {percentual:.2f}% — "
                    "acima da tolerância de 5%."
                ),
                parecer_sugerido=REVISAO_HUMANA,
                pendencia=(
                    "Conferir as áreas na matrícula e no CAR, corrigir o documento "
                    "divergente e reapresentar a proposta."
                ),
            ),
            f"Divergência de {percentual:.2f}% entre matrícula e CAR (acima de 5%).",
        )
    return (
        None,
        f"Divergência de {percentual:.2f}% entre matrícula e CAR (dentro da tolerância de 5%).",
    )
