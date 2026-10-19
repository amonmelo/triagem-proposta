"""Tipos, constantes e utilidades compartilhadas da triagem.

Os valores de parecer em JSON são ASCII ("REVISAO_HUMANA"); o card em
Markdown renderiza a forma acentuada ("REVISÃO HUMANA") — ver `ROTULOS`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

SEGUE = "SEGUE"
RECUSADA = "RECUSADA"
REVISAO_HUMANA = "REVISAO_HUMANA"

# Gravidade de cada parecer: a decisão final é sempre a PIOR violação.
# (RECUSADA vence REVISÃO HUMANA, que vence SEGUE — seção 3 do teste.)
_GRAVIDADE = {SEGUE: 0, REVISAO_HUMANA: 1, RECUSADA: 2}

ROTULOS = {SEGUE: "SEGUE", RECUSADA: "RECUSADA", REVISAO_HUMANA: "REVISÃO HUMANA"}


def pior_parecer(*pareceres: str) -> str:
    """Devolve o parecer mais grave entre os informados."""
    return max(pareceres, key=lambda p: _GRAVIDADE[p])


# Os 7 campos obrigatórios são exatamente os do formato sugerido na seção 4.
CAMPOS_OBRIGATORIOS = (
    "id",
    "area_degradada_ha",
    "area_matricula_ha",
    "area_car_ha",
    "alerta_desmatamento",
    "situacao_car",
    "situacao_cadastral",
)

# Constantes das regras — mudar aqui é mudar a política (ver DESIGN.md).
AREA_MINIMA_DEGRADADA_HA = 100.0        # R1: "pelo menos 100 ha"
CORTE_DESMATAMENTO = date(2020, 1, 1)   # R2: recusa alerta ESTRITAMENTE posterior
TOLERANCIA_AREA_PERCENTUAL = 5.0        # R5: diferença MAIOR que 5% vai para revisão


@dataclass(frozen=True)
class Violacao:
    """Uma regra que falhou, com o parecer que ela sozinha produziria."""

    regra: str
    mensagem: str
    parecer_sugerido: str  # SEGUE nunca aparece aqui; só RECUSADA ou REVISAO_HUMANA
    pendencia: Optional[str] = None  # ação concreta para o card de revisão humana


@dataclass(frozen=True)
class ResultadoRegra:
    """Como uma regra foi avaliada (para o relatório completo do parecer)."""

    regra: str
    resultado: str  # "ok" | "violacao" | "nao_avaliada"
    detalhe: str
    violacao: Optional[Violacao] = None


@dataclass
class Parecer:
    """Resultado completo da triagem de uma proposta."""

    proposta_id: str
    parecer: str
    motivos: list  # list[Violacao], em ordem de regra (R1..R6)
    pendencias: list  # list[dict] {"regra", "acao"} — vazia salvo em REVISAO_HUMANA
    regras: list  # list[ResultadoRegra], em ordem R1..R6

    def to_dict(self) -> dict:
        return {
            "esquema": "triagem-proposta/1",
            "proposta_id": self.proposta_id,
            "parecer": self.parecer,
            "motivos": [
                {"regra": v.regra, "mensagem": v.mensagem} for v in self.motivos
            ],
            "pendencias": list(self.pendencias),
            "regras": [
                {
                    "regra": r.regra,
                    "resultado": r.resultado,
                    "detalhe": r.detalhe,
                }
                for r in self.regras
            ],
        }


class EntradaInvalida(Exception):
    """A entrada não é uma proposta triável (ex.: JSON que não é um objeto)."""


def fmt_num(valor: float) -> str:
    """Formata números de área sem ruído e com vírgula: 850.0 -> "850", 99.5 -> "99,5"."""
    if float(valor).is_integer():
        return str(int(valor))
    return f"{valor:g}".replace(".", ",")


def fmt_pct(valor: float) -> str:
    """Percentual com duas casas e vírgula decimal: 11.111 -> "11,11%"."""
    return f"{valor:.2f}%".replace(".", ",")


def normalizar_texto(valor: str) -> str:
    """Minúsculas + espaços colapsados (esclarecimento da regra R3)."""
    return " ".join(valor.split()).casefold()


def citar(valor: Any) -> str:
    """Representa o valor recebido para citar em mensagens (JSON seguro)."""
    return json.dumps(valor, ensure_ascii=False)
